// End-to-end smoke test for the generated multi-project workbench.
// Run: NODE_PATH=/path/to/node_modules node test_workbench.mjs
// jsdom is the sole test dependency; NODE_PATH is useful when it is installed outside this repo.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let JSDOM;
let VirtualConsole;
try {
  const searchPaths = [process.cwd(), ...(process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean)];
  ({ JSDOM, VirtualConsole } = require(require.resolve('jsdom', { paths: searchPaths })));
} catch {
  console.error('缺少 jsdom。请安装到本项目，或设置 NODE_PATH 指向含 jsdom 的 node_modules。');
  process.exit(2);
}

const root = path.dirname(fileURLToPath(import.meta.url));
const page = path.join(root, 'fde-hub-site', 'workbench.html');
// Exercise the editable script against the generated page's injected project data.
// This also lets the workbench test run before the full site is rebuilt.
const script = path.join(root, 'assets', 'workbench.js');
let html = readFileSync(page, 'utf8');
assert.match(html, /window\.WB_DATA=/, '页面必须注入项目数据');
assert.match(html, /<script src="assets\/workbench\.js"><\/script>/, '页面必须加载工作台脚本');
html = html.replace('<script src="assets/workbench.js"></script>',
  `<script>${readFileSync(script, 'utf8')}</script>`);
html = html.replace('<script src="assets/hub.js"></script>', '');

const scriptErrors = [];
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', e => scriptErrors.push(e.message));
virtualConsole.on('error', e => scriptErrors.push(String(e)));
const dom = new JSDOM(html, {
  url: 'http://localhost/workbench.html',
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  virtualConsole,
});
const { window } = dom;
const { document, localStorage } = window;
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const content = () => $('#wb-view').textContent;
const saved = key => JSON.parse(localStorage.getItem(key));
const visit = hash => {
  window.location.hash = hash;
  window.dispatchEvent(new window.Event('hashchange'));
};
const check = (name, fn) => {
  const result = fn();
  if (result && typeof result.then === 'function') {
    return result.then(() => console.log('  ✓ ' + name));
  }
  console.log('  ✓ ' + name);
};
const p1 = window.WB_DATA.projects[0];
const p2 = window.WB_DATA.projects[1];
assert.ok(p1 && p2, '测试需要至少两个项目');
assert.ok(p1.stages.length && p1.quiz.length && p2.stages.length, '项目需要任务和诊断数据');
const s1 = p1.stages[0];
const s2 = p2.stages[0];
const p1Route = suffix => `#p/${p1.id}${suffix}`;
const p2Route = suffix => `#p/${p2.id}${suffix}`;
const alerts = [];
window.alert = message => alerts.push(message);
window.confirm = () => true;

check('首次进入确认目标，展示多个项目入口', () => {
  assert.ok($('#wb-goal'));
  $('#wb-goal').value = 'job';
  $('#wb-bg').value = 'backend';
  $('#wb-pilot').value = 'P99';
  $('#wb-go').click();
  const prof = saved('wb_profile');
  assert.equal(prof.goal, 'job');
  assert.equal(prof.background, 'backend');
  assert.equal(prof.pilot, 'P99');
  assert.equal(prof.v, 2);
  assert.ok(content().includes(window.WB_DATA.routing.default.note));
  for (const project of [p1, p2]) {
    assert.ok(content().includes(project.title));
    assert.ok($(`a[href="#p/${project.id}"]`));
  }
});

check('进入项目，自适应诊断逐级出题，结果仅为能力线索', () => {
  visit(p1Route(''));
  assert.ok(content().includes(s1.title));
  visit(p1Route('/diag'));
  const qmap = Object.fromEntries(p1.quiz.map(q => [q.id, q]));
  let guard = 0;
  while (!$('.wb-self')) {
    const qEl = $('.wb-q');
    assert.ok(qEl, '自适应流程应一题一屏');
    const q = qmap[qEl.getAttribute('data-qid')];
    assert.ok(q, '当前题目应来自题库');
    $(`input[name="${q.id}"][value="${q.ans}"]`).checked = true;
    $('#wb-next-q').click();
    assert.ok(++guard < 40, '自适应流程应在有限步内结束');
  }
  $('.wb-self input').checked = true;
  $('#wb-submit-diag').click();
  const diagnosis = saved(`wb_diag_${p1.id}`);
  assert.equal(diagnosis.done, true);
  assert.equal(diagnosis.v, 2);
  for (const d of window.WB_DATA.dims) {
    assert.equal(diagnosis.levels[d.id], 2, `全答对时 ${d.id} 应定级为 2`);
  }
  assert.ok(diagnosis.result && diagnosis.result.business, 'result 结构保持兼容');
  assert.ok(content().includes('上次诊断结果'));
  assert.ok(content().includes('误区'), '结果页应出现误区提示区');
  assert.equal($('.ds3'), null, '诊断不能直接生成阶段自评记录');
  assert.equal(saved(`wb_diag_${p2.id}`), null, '诊断按项目隔离');
  assert.equal(diagnosis.lowConf, true, 'jsdom 中极速全对应标记为低可信');
  assert.equal(saved('wb_overrides'), null, '未点关闭前不应产生 overrides 记录');
  visit(p1Route(''));
  assert.ok(!content().includes('路径建议（基于诊断线索）'), '低可信诊断不应出路径建议卡');
  assert.ok(content().includes('低可信'), '低可信诊断应改为提示文案');
});

check('提交任务，格式提示和待自评状态落库', () => {
  visit(p1Route(`/task-${s1.id}`));
  assert.ok(content().includes('① 任务目标与自检参考'));
  assert.ok(content().includes('② 资料与辅导'));
  assert.ok(content().includes('③ 提交与自评反馈'));
  assert.equal($$('.wb-res').length, s1.resources.length);
  $('#wb-submit').click();
  assert.match(alerts.pop(), /请先粘贴/);
  $('#wb-artifact').value = '用户：云帆科技客服新人，每天查资料。\n业务基线：找答案平均 25 分钟。\n非目标：不做实时数据接入，也不做跨语言检索。\n成功标准：平均找答案时间降到 5 分钟。';
  $('#wb-artifact').dispatchEvent(new window.Event('change'));
  assert.equal(saved(`wb_stages_${p1.id}`)[s1.id].status, 'in_progress');
  $('#wb-submit').click();
  assert.match(content(), new RegExp(`格式检查：${s1.auto.length}/${s1.auto.length}`));
  assert.ok(content().includes('待自评'));
  assert.equal($$('.wb-ritem').length, s1.rubric.length);
  assert.equal(saved(`wb_stages_${p1.id}`)[s1.id].versions.length, 1);
});

check('自评清单缺依据或迁移思考未答时不能完成，补齐后保存记录', () => {
  $$('.wb-ritem').forEach((item, i) => {
    item.querySelector('.wb-r-ok').checked = true;
    if (i < s1.rubric.length - 1) item.querySelector('.wb-r-ev').value = `证据 ${i + 1}：需求说明对应段落`;
  });
  $('#wb-finish').click();
  assert.equal(saved(`wb_stages_${p1.id}`)[s1.id].status, 'revise');
  assert.ok(content().includes('1 项尚未勾选或填写依据'));
  const last = $$('.wb-ritem').at(-1);
  last.querySelector('.wb-r-ev').value = '证据：成功标准段落的基线和目标';
  $('#wb-finish').click();
  assert.equal(saved(`wb_stages_${p1.id}`)[s1.id].status, 'revise');
  assert.ok(content().includes('迁移思考未作答'));
  $('#wb-variant').value = '先问谁使用、当前怎样处理、第一版的成功指标是什么。';
  $('#wb-finish').click();
  const stage = saved(`wb_stages_${p1.id}`)[s1.id];
  assert.equal(stage.status, 'passed');
  assert.equal(stage.versions[0].rubric.length, s1.rubric.length);
  assert.equal(stage.versions[0].evidN, s1.rubric.length);
  assert.ok(stage.versions[0].variantAns);
  assert.ok(content().includes('本阶段已完成自评'));
});

check('学习记录和今日任务反映已保存自评及后续阶段', () => {
  visit(p1Route('/skills'));
  assert.ok(content().includes('已有自评记录'));
  assert.ok(content().includes('自评记录'));
  assert.ok(content().includes(`${s1.title} v1`));
  assert.equal($$('.wb-scard .ds3').length, 1, '只有完成自评的维度显示已保存记录');
  assert.ok($$('.wb-scard .ds1').length > 0, '诊断线索不升级为阶段自评记录');
  visit(p1Route(''));
  assert.ok(content().includes(p1.stages[1].title));
  assert.ok(content().includes(`1 / ${p1.stages.length} 阶段自评完成`));
});

check('第二项目独立存储，并保留在帮助下完成标记', () => {
  visit(p2Route(''));
  assert.ok(content().includes(s2.title));
  assert.ok(content().includes(`0 / ${p2.stages.length} 阶段自评完成`));
  visit(p2Route(`/task-${s2.id}`));
  $('#wb-artifact').value = '第二项目的交付说明及现场测试证据。';
  $('#wb-helped').checked = true;
  $('#wb-submit').click();
  $$('.wb-ritem').forEach((item, i) => {
    item.querySelector('.wb-r-ok').checked = true;
    item.querySelector('.wb-r-ev').value = `证据 ${i + 1}：交付说明第 ${i + 1} 节`;
  });
  $('#wb-variant').value = '先核对业务边界，再与客户确认验收依据。';
  $('#wb-finish').click();
  const assisted = saved(`wb_stages_${p2.id}`)[s2.id];
  assert.equal(assisted.status, 'passed');
  assert.equal(assisted.versions[0].helped, true);
  visit(p2Route('/skills'));
  assert.ok(content().includes('自报在帮助下完成'));
  assert.equal(saved(`wb_stages_${p1.id}`)[s1.id].status, 'passed');
});

await check('导出的 JSON 含全部项目的诊断、版本、量表及帮助标记', async () => {
  let exportedBlob;
  let downloadName;
  window.URL.createObjectURL = blob => { exportedBlob = blob; return 'blob:workbench-test'; };
  window.HTMLAnchorElement.prototype.click = function () { downloadName = this.download; };
  visit(p1Route('/data'));
  $('#wb-export').click();
  assert.equal(downloadName, 'fde-workbench-backup.json');
  assert.ok(content().includes('已导出'));
  const json = await new Promise((resolve, reject) => {
    const reader = new window.FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(exportedBlob);
  });
  const dump = JSON.parse(json);
  assert.equal(Object.keys(dump.projects).length, window.WB_DATA.projects.length);
  assert.equal(dump.profile.goal, 'job');
  assert.equal(dump.projects[p1.id].diag.done, true);
  assert.equal(dump.projects[p1.id].stages[s1.id].versions[0].evidN, s1.rubric.length);
  assert.equal(dump.projects[p2.id].stages[s2.id].versions[0].helped, true);
});

assert.deepEqual(scriptErrors, [], '浏览器脚本不应报错');
dom.window.close();
console.log('\n结果：7 项端到端检查通过');
