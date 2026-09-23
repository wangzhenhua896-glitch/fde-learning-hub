// Domain model, evidence updates, and explainable recommendation v1. No DOM or storage access.
export const PROFILE_VERSION = 1;
export const FORMATS = ['micro_lesson','deep_dive','worked_example','interactive_quiz','flash_review','guided_lab','challenge_lab','capstone','real_world_fde_case','jd_skill_drill'];
export function freshProfile(overrides = {}) {
  return {schemaVersion: PROFILE_VERSION, anonymous: true, role:'fde', industry:'general', region:'china', company:'', targetSkills:[], background:'novice', language:'zh-CN', minutesPerDay:15, preferences:{format:'mixed'}, selfAssessment:{}, diagnostic:{}, mastery:{}, weakSkills:[], pace:{attempts:0, successes:0}, completed:[], attempts:{}, reviewQueue:[], history:[], streak:{lastDay:'',days:0}, onboarding:'new', demo:false, ...overrides};
}
export function validateContent(content) {
  const skills = new Set(content.skills.map(s => s.id));
  const units = new Set(content.units.map(u => u.id));
  if (skills.size !== content.skills.length || units.size !== content.units.length) throw Error('重复的 skill 或 unit ID');
  for (const s of content.skills) if ((s.prerequisites || []).some(p => !skills.has(p))) throw Error(`${s.id} 的技能先修引用无效`);
  for (const u of content.units) {
    for (const key of ['prerequisites','skills','difficulty','estimated_time','format','evidence_of_mastery','next_candidates','review_policy']) if (u[key] === undefined) throw Error(`${u.id} 缺少 ${key}`);
    if (!FORMATS.includes(u.format)) throw Error(`${u.id} 格式无效`);
    if ((u.resources || []).some(r => !/^[a-z0-9-]+\.html$/.test(r.url))) throw Error(`${u.id} 资料链接无效`);
    if (u.skills.some(s => !skills.has(s)) || u.prerequisites.some(p => !units.has(p)) || u.next_candidates.some(n => !units.has(n))) throw Error(`${u.id} 引用无效`);
    if (u.lab_template && !content.labTemplates[u.lab_template]) throw Error(`${u.id} 的 lab 模板不存在`);
  }
  const visiting = new Set(), visited = new Set(), map = new Map(content.units.map(u => [u.id,u]));
  function walk(id) { if (visiting.has(id)) throw Error('内容图存在循环'); if (visited.has(id)) return; visiting.add(id); map.get(id).prerequisites.forEach(walk); visiting.delete(id); visited.add(id); }
  content.units.forEach(u => walk(u.id));
  const smap=new Map(content.skills.map(s=>[s.id,s])), sv=new Set(), sd=new Set();
  function swalk(id) {if(sv.has(id)) throw Error('技能图存在循环');if(sd.has(id)) return;sv.add(id);(smap.get(id).prerequisites||[]).forEach(swalk);sv.delete(id);sd.add(id);}
  content.skills.forEach(s=>swalk(s.id));
  return true;
}
export function mastery(profile, skill) { return profile.mastery[skill] || {score:0, state:'unseen', lastEvidence:null, failures:0}; }
export function applyEvidence(profile, unit, evidence, now = Date.now()) {
  const p = structuredClone(profile), ok = !!evidence.passed, kind = evidence.kind || 'quiz';
  const n = (p.attempts[unit.id] || 0) + 1; p.attempts[unit.id] = n;
  if (ok && kind !== 'diagnostic' && !p.completed.includes(unit.id)) p.completed.push(unit.id);
  for (const skill of unit.skills) {
    const old = mastery(p, skill), gain = kind === 'lab' ? 22 : kind === 'diagnostic' ? 12 : 14;
    const score = Math.max(0, Math.min(100, old.score + (ok ? gain : -Math.max(8, Math.round(old.score * .16)))));
    const rank = {unseen:0,exposure:1,practiced:2,demonstrated:3,retained:4};
    const candidate = ok ? (kind === 'lab' ? 'demonstrated' : kind === 'review' ? 'retained' : 'practiced') : old.state === 'unseen' ? 'exposure' : old.state;
    const state = rank[candidate] > rank[old.state] ? candidate : old.state;
    p.mastery[skill] = {score,state,lastEvidence:{unitId:unit.id,kind,passed:ok,at:now},failures:ok ? 0 : old.failures + 1};
    if (!ok && !p.weakSkills.includes(skill)) p.weakSkills.push(skill);
    if (ok) p.weakSkills = p.weakSkills.filter(x => x !== skill);
  }
  p.pace.attempts++; if (ok) p.pace.successes++;
  p.history.push({type:'assessment',unitId:unit.id,kind,passed:ok,at:now,attempt:n,hintsUsed:evidence.hintsUsed || 0,errorType:evidence.errorType || null,tests:evidence.tests || []});
  p.history = p.history.slice(-200);
  if (ok && kind !== 'diagnostic') {
    const days = unit.review_policy.after_days || [1,3,7], prior = p.reviewQueue.find(r => r.unitId === unit.id), interval = Math.min(prior ? prior.interval + 1 : 0, days.length - 1);
    p.reviewQueue = p.reviewQueue.filter(r => r.unitId !== unit.id);
    p.reviewQueue.push({unitId:unit.id, dueAt:now + days[interval] * 86400000, interval});
  }
  const day = new Date(now).toISOString().slice(0,10), prev = p.streak.lastDay;
  if (prev !== day) { p.streak.days = prev && (Date.parse(day) - Date.parse(prev)) === 86400000 ? p.streak.days + 1 : 1; p.streak.lastDay = day; }
  return p;
}
export function applyDiagnostic(profile, answers, content, now = Date.now()) {
  let p = structuredClone(profile); p.diagnostic = {answers,at:now}; p.onboarding = 'ready';
  for (const [unitId, correct] of Object.entries(answers)) { const u = content.units.find(x => x.id === unitId); if (u) p = applyEvidence(p,u,{kind:'diagnostic',passed:correct},now); }
  return p;
}
export function importWorkbenchSignals(profile, raw) {
  const p = structuredClone(profile), dimMap = {business:'discovery',data:'integration',ai:'rag',evals:'eval',ops:'deployment',comm:'discovery'};
  const d = raw?.result || {};
  for (const [dim, record] of Object.entries(d)) {
    const id = dimMap[dim]; if (!id || !record?.n) continue;
    const inferred = Math.round(40 * record.ok / record.n);
    if (inferred > mastery(p,id).score) p.mastery[id] = {score:inferred,state:'exposure',lastEvidence:{kind:'legacy_diagnostic',at:raw.ts || null},failures:0};
  }
  return p;
}
export function importWorkbenchSelfReports(profile, stages) {
  const p = structuredClone(profile);
  const mapping = {s1:'discovery',s2:'integration',s3:'rag',s4:'rag',s5:'eval',s6:'deployment',s7:'discovery'};
  for (const [stageId, record] of Object.entries(stages || {})) {
    if (record?.status !== 'passed' || !mapping[stageId]) continue;
    const id = mapping[stageId], old = mastery(p,id);
    p.mastery[id] = {score:Math.max(old.score,45),state:'practiced',lastEvidence:{kind:'legacy_self_report',at:record.versions?.at(-1)?.ts || null},failures:0};
  }
  return p;
}
export function skillsFromJD(text) {
  const patterns = {discovery:/需求|客户|stakeholder|discovery/i,llm:/大模型|LLM|prompt/i,python:/python|pandas/i,integration:/集成|API|integration|数据接入/i,rag:/RAG|检索|向量/i,eval:/评测|评估|eval/i,agent:/agent|智能体/i,deployment:/部署|Docker|Kubernetes|CI\/CD|监控/i};
  return Object.entries(patterns).filter(([,re]) => re.test(text || '')).map(([id]) => id);
}
export function recommend(profile, content, now = Date.now()) {
  const targets = {...(content.roleTargets[profile.role] || content.roleTargets.fde)};
  const industryFocus = {finance:['integration','eval'],retail:['rag','discovery'],healthcare:['integration','eval'],saas:['agent','integration']}[profile.industry] || [];
  for (const id of industryFocus) targets[id] = Math.min(100,(targets[id] || 50) + 10);
  for (const id of profile.targetSkills || []) if (id in targets) targets[id] = Math.min(100,targets[id] + 15);
  const map = new Map(content.units.map(u => [u.id,u]));
  const done = new Set(profile.completed);
  const eligible = u => u.prerequisites.every(id => done.has(id) || map.get(id).skills.every(s => mastery(profile,s).score >= 65)) && u.skills.every(id => (content.skills.find(s=>s.id===id)?.prerequisites || []).every(pre => mastery(profile,pre).score >= 10));
  const due = profile.reviewQueue.filter(r => r.dueAt <= now && map.has(r.unitId)).sort((a,b) => a.dueAt - b.dueAt);
  if (due.length) { const u = map.get(due[0].unitId); return {unit:u,action:'review',reason:`${u.skills.map(s => content.skills.find(x => x.id === s)?.name).join('、')}到了短复习时间，巩固已学内容。`,unlock:u.next_candidates}; }
  const stuck = Object.entries(profile.attempts).find(([id,n]) => n >= 2 && !done.has(id));
  if (stuck) {
    const failed = map.get(stuck[0]);
    const lower = content.units.find(u => failed && u.difficulty < failed.difficulty && (u.skills.some(s => failed.skills.includes(s)) || failed.prerequisites.includes(u.id)) && eligible(u));
    const failedAt = Math.max(0,...profile.history.filter(e => e.unitId === stuck[0] && !e.passed).map(e => e.at));
    const repaired = lower && profile.history.some(e => e.unitId === lower.id && e.passed && e.at > failedAt);
    if (lower && !repaired) return {unit:lower,action:'remediate',reason:`你在「${failed.title}」连续遇到困难，先用 ${lower.estimated_time} 分钟补基础。`,unlock:lower.next_candidates};
  }
  const candidates = content.units.filter(u => !done.has(u.id) && eligible(u) && !u.skills.every(s => mastery(profile,s).score >= (targets[s] || 60) + 10));
  const scored = candidates.map(u => {
    const gap = Math.max(...u.skills.map(s => Math.max(0,(targets[s] || 50) - mastery(profile,s).score)));
    const level = Math.min(...u.skills.map(s => mastery(profile,s).score));
    const market = profile.region === 'china' ? Math.max(...u.skills.map(s => content.market.weights[s] || 0)) : 0;
    const failures = profile.attempts[u.id] || 0;
    const weak = u.skills.some(s => profile.weakSkills.includes(s));
    const fit = u.estimated_time <= profile.minutesPerDay ? 12 : 0;
    const formatFit = ({micro_lesson:level<30?8:0,worked_example:level>=20&&level<60?6:0,deep_dive:level>=25?4:0,interactive_quiz:level>=25?5:0,flash_review:level>=35?5:0,guided_lab:level>=30?8:0,challenge_lab:level>=50?8:0,capstone:level>=60?8:0,real_world_fde_case:level>=20?5:0,jd_skill_drill:u.skills.some(s=>(profile.targetSkills||[]).includes(s))?10:0})[u.format] || 0;
    const preferred = profile.preferences?.format === u.format ? 4 : 0;
    const score = gap + market * .16 + fit + formatFit + preferred + (weak ? 18 : 0) - failures * 15 - u.difficulty * 3;
    return {u,score,gap,market,weak};
  }).sort((a,b) => b.score - a.score || a.u.id.localeCompare(b.u.id));
  if (!scored.length) return {unit:null,action:'complete',reason:'当前目标的学习单元已完成。可以调整目标或探索资料。',unlock:[]};
  let pick = scored[0];
  let reason = pick.weak ? `因为${pick.u.skills.map(s => content.skills.find(x => x.id === s)?.name).join('、')}需要补强，先做这一步。` : `你的目标是 ${profile.role.toUpperCase()}，这一步补上当前技能差距。`;
  if (pick.u.skills.some(s => (profile.targetSkills || []).includes(s))) reason += ' 你提供的岗位描述提到了相关技能。';
  if (pick.market >= 20) reason += ` 历史岗位样本中约 ${pick.market}% 提到相关技能。`;
  return {unit:pick.u,action:pick.weak ? 'remediate' : 'continue',reason,unlock:pick.u.next_candidates};
}
export function demoProfile(persona) {
  const p = freshProfile({role:persona.role,background:persona.background,onboarding:'ready',demo:true});
  for (const [id,score] of Object.entries(persona.mastery)) p.mastery[id] = {score,state:'exposure',lastEvidence:{kind:'demo',at:null},failures:0};
  return p;
}
