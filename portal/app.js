/* ══════════ FIREBASE CONFIG ══════════ */
const firebaseConfig = {
  apiKey: "AIzaSyCHXYfgfM83wpHemsSySFbV6KLrGF5RAaw",
  authDomain: "social-media-images-agent.firebaseapp.com",
  projectId: "social-media-images-agent",
  storageBucket: "social-media-images-agent.firebasestorage.app",
  messagingSenderId: "242719684566",
  appId: "1:242719684566:web:9a83a7634fe61958ac9677",
  measurementId: "G-KRKKJ0X1TE"
};
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const googleProvider = new firebase.auth.GoogleAuthProvider();

/* ══════════ CONFIG — SET YOUR n8n URL HERE ══════════ */
const API_BASE = 'http://localhost:3000/api';
let firebaseToken = '';
let clients = [];
let currentStep = 1;
const TOTAL_STEPS = 4;

/* ══════════ AUTH ══════════ */
function toggleAuthMode(e) {
  e.preventDefault();
  const si = document.getElementById('signin-form');
  const su = document.getElementById('signup-form');
  si.style.display = si.style.display === 'none' ? '' : 'none';
  su.style.display = su.style.display === 'none' ? '' : 'none';
}

document.getElementById('signin-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('signin-btn');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    await auth.signInWithEmailAndPassword(v('si-email'), v('si-password'));
  } catch (err) { showLoginError(err.message); }
  btn.disabled = false; btn.innerHTML = '<span>Sign In</span><i class="fa-solid fa-arrow-right"></i>';
});

document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('signup-btn');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    await auth.createUserWithEmailAndPassword(v('su-email'), v('su-password'));
  } catch (err) { showLoginError(err.message); }
  btn.disabled = false; btn.innerHTML = '<span>Create Account</span><i class="fa-solid fa-arrow-right"></i>';
});

async function googleSignIn() {
  try { await auth.signInWithPopup(googleProvider); }
  catch (err) { showLoginError(err.message); }
}

function showLoginError(msg) {
  const el = document.getElementById('login-error');
  el.textContent = msg; el.style.display = 'block';
}

auth.onAuthStateChanged(async (user) => {
  if (user) {
    firebaseToken = await user.getIdToken();
    enterApp(user);
  } else {
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
  }
});

function enterApp(user) {
  document.getElementById('login-screen').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  document.getElementById('user-email-display').textContent = user.email || user.displayName || '';
  loadClients();
}

function logout() {
  auth.signOut();
  firebaseToken = '';
}

/* ══════════ API ══════════ */
async function apiCall(path, method = 'POST', body = null) {
  if (auth.currentUser) firebaseToken = await auth.currentUser.getIdToken();
  const opts = { method, headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + firebaseToken } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API_BASE + path, opts);
  return res.json();
}

async function loadClients() {
  try {
    const data = await apiCall('/clients', 'GET');
    if (data.success && data.clients) {
      clients = data.clients;
      renderDashboard();
    }
  } catch (e) { toast('Failed to load clients', 'error'); }
}

/* ══════════ DASHBOARD ══════════ */
function renderDashboard() {
  const active = clients.filter(c => c.is_active);
  document.getElementById('stat-total').textContent = clients.length;
  document.getElementById('stat-active').textContent = active.length;
  document.getElementById('stat-inactive').textContent = clients.length - active.length;
  const grid = document.getElementById('clients-grid');
  if (!clients.length) {
    grid.innerHTML = '<div class="empty-state"><i class="fa-solid fa-store"></i><h4>No clients yet</h4><p>Add your first client</p><button class="btn btn-primary" onclick="showView(\'add-client\')"><i class="fa-solid fa-plus"></i>Add Client</button></div>';
    return;
  }
  grid.innerHTML = clients.map(c => `
    <div class="client-card" data-id="${c.client_id}">
      <div class="client-card-header"><div><div class="client-name">${esc(c.business_name)}</div><div class="client-location"><i class="fa-solid fa-location-dot"></i> ${esc(c.location||'—')}</div></div>
      <span class="client-badge ${c.is_active?'active':'inactive'}">${c.is_active?'Active':'Inactive'}</span></div>
      <div class="client-meta">
        <div class="client-meta-item"><i class="fa-brands fa-whatsapp"></i>${esc(c.phone_primary||'—')}</div>
        <div class="client-meta-item"><i class="fa-solid fa-tag"></i>${esc(c.brand_category||'general')}</div>
        <div class="client-meta-item"><i class="fa-solid fa-calendar"></i>Est. ${esc(c.established_year||'—')}</div>
      </div>
      <div class="client-actions">
        <button class="btn btn-ghost btn-sm" onclick="editClient('${c.client_id}')"><i class="fa-solid fa-pen"></i>Edit</button>
        <button class="btn btn-ghost btn-sm" onclick="toggleClient('${c.client_id}',${c.is_active})"><i class="fa-solid fa-${c.is_active?'pause':'play'}"></i>${c.is_active?'Pause':'Enable'}</button>
        <button class="btn btn-ghost btn-sm" onclick="deleteClient('${c.client_id}','${esc(c.business_name)}')"><i class="fa-solid fa-trash"></i></button>
      </div>
    </div>`).join('');
}

function filterClients() {
  const q = v('client-search').toLowerCase();
  document.querySelectorAll('.client-card').forEach(c => {
    c.style.display = (c.querySelector('.client-name')?.textContent?.toLowerCase()||'').includes(q) ? '' : 'none';
  });
}

/* ══════════ NAVIGATION ══════════ */
function showView(view) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-'+view).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`[data-view="${view}"]`)?.classList.add('active');
  if (view === 'add-client') resetForm();
  if (view === 'dashboard') loadClients();
}
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', e => { e.preventDefault(); showView(item.dataset.view); });
});

/* ══════════ WIZARD ══════════ */
function wizardNext() { if (currentStep < TOTAL_STEPS) setStep(currentStep + 1); }
function wizardPrev() { if (currentStep > 1) setStep(currentStep - 1); }
function setStep(n) {
  currentStep = n;
  document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
  document.querySelector(`.form-step[data-step="${n}"]`).classList.add('active');
  document.querySelectorAll('.wizard-step').forEach(s => {
    const step = +s.dataset.step; s.classList.remove('active','completed');
    if (step === n) s.classList.add('active'); else if (step < n) s.classList.add('completed');
  });
  document.getElementById('btn-prev').style.display = n > 1 ? '' : 'none';
  document.getElementById('btn-next').style.display = n < TOTAL_STEPS ? '' : 'none';
  document.getElementById('btn-submit').style.display = n === TOTAL_STEPS ? '' : 'none';
}

/* ══════════ COLOR PICKERS ══════════ */
['primary','secondary','accent','bg'].forEach(k => {
  const el = document.getElementById('cf-color-'+k);
  if (el) el.addEventListener('input', () => { document.getElementById('cf-color-'+k+'-hex').textContent = el.value.toUpperCase(); });
});

/* ══════════ FORM SUBMIT ══════════ */
document.getElementById('client-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const editId = v('edit-client-id');
  const payload = gatherFormData();
  const btn = document.getElementById('btn-submit');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Saving...';
  try {
    const isEditing = !!editId;
    const endpoint = '/clients';
    const method = isEditing ? 'PUT' : 'POST';
    if (editId) payload.client_id = editId;
    payload.firebase_uid = auth.currentUser?.uid || '';
    
    const data = await apiCall(endpoint, method, payload);
    if (data.success) { toast(editId ? 'Updated!' : 'Registered!', 'success'); showView('dashboard'); }
    else toast(data.message || 'Failed', 'error');
  } catch (ex) { toast('Network error', 'error'); }
  btn.disabled = false;
  btn.innerHTML = `<i class="fa-solid fa-check"></i><span id="btn-submit-text">${editId ? 'Update' : 'Register'} Client</span>`;
});

function gatherFormData() {
  return {
    business_name: v('cf-business-name'), tagline: v('cf-tagline'), established_year: v('cf-established'),
    location: v('cf-location'), brand_category: v('cf-category'), brand_positioning: v('cf-positioning'),
    phone_primary: v('cf-phone-primary'), phone_display: v('cf-phone-display'),
    wa_phone_id: v('cf-wa-phone-id'), wa_token: v('cf-wa-token'),
    fb_page_id: v('cf-fb-page-id'), fb_access_token: v('cf-fb-token'),
    ig_node_id: v('cf-ig-node-id'), ig_credential_id: v('cf-ig-credential-id'),
    kie_api_key: v('cf-kie-key'), imgbb_api_key: v('cf-imgbb-key'),
    serp_api_key: v('cf-serp-key'), calendarific_api_key: v('cf-calendar-key'),
    daily_cron: v('cf-cron'), timezone: v('cf-timezone'),
    prompt_poster: v('cf-prompt-poster'), prompt_enhance: v('cf-prompt-enhance'),
    prompt_planner: v('cf-prompt-planner'), prompt_morning: v('cf-prompt-morning'), prompt_welcome: v('cf-prompt-welcome')
  };
}

/* ══════════ EDIT ══════════ */
function editClient(id) {
  const c = clients.find(x => x.client_id === id); if (!c) return;
  showView('add-client');
  document.getElementById('form-title').textContent = 'Edit Client';
  document.getElementById('form-subtitle').textContent = 'Update ' + c.business_name;
  document.getElementById('edit-client-id').value = c.client_id;
  document.getElementById('btn-submit-text').textContent = 'Update Client';
  const map = {
    'cf-business-name':c.business_name,'cf-tagline':c.tagline,'cf-established':c.established_year,
    'cf-location':c.location,'cf-category':c.brand_category,'cf-positioning':c.brand_positioning,
    'cf-phone-primary':c.phone_primary,'cf-phone-display':c.phone_display,
    'cf-wa-phone-id':c.wa_phone_id,'cf-wa-token':c.wa_token,
    'cf-fb-page-id':c.fb_page_id,'cf-fb-token':c.fb_access_token,
    'cf-ig-node-id':c.ig_node_id,'cf-ig-credential-id':c.ig_credential_id,
    'cf-kie-key':c.kie_api_key,'cf-imgbb-key':c.imgbb_api_key,
    'cf-serp-key':c.serp_api_key,'cf-calendar-key':c.calendarific_api_key,
    'cf-cron':c.daily_cron||'0 12 * * 1-6','cf-timezone':c.timezone||'Asia/Kolkata',
    'cf-prompt-poster':c.prompt_poster,'cf-prompt-enhance':c.prompt_enhance,
    'cf-prompt-planner':c.prompt_planner,'cf-prompt-morning':c.prompt_morning,'cf-prompt-welcome':c.prompt_welcome
  };
  Object.entries(map).forEach(([id,val]) => setV(id, val));
}

function resetForm() {
  document.getElementById('client-form').reset();
  document.getElementById('edit-client-id').value = '';
  document.getElementById('form-title').textContent = 'Register New Client';
  document.getElementById('form-subtitle').textContent = 'Complete all steps to configure automation';
  document.getElementById('btn-submit-text').textContent = 'Register Client';
  setStep(1);
}

/* ══════════ TOGGLE/DELETE ══════════ */
async function toggleClient(id, isActive) {
  try { const d = await apiCall(`/clients/${id}/toggle`,'PATCH',{is_active:!isActive});
    if(d.success){toast(isActive?'Paused':'Enabled','success');loadClients();}else toast(d.message,'error');
  } catch(e){toast('Error','error');}
}
function deleteClient(id, name) {
  document.getElementById('modal-title').textContent = 'Delete Client';
  document.getElementById('modal-message').textContent = `Delete "${name}"? This cannot be undone.`;
  document.getElementById('confirm-modal').style.display = 'flex';
  document.getElementById('modal-confirm-btn').onclick = async () => {
    closeModal();
    try { const d = await apiCall(`/clients/${id}`,'DELETE');
      if(d.success){toast('Deleted','success');loadClients();}else toast(d.message,'error');
    } catch(e){toast('Error','error');}
  };
}
function closeModal() { document.getElementById('confirm-modal').style.display = 'none'; }

/* ══════════ SETTINGS ══════════ */
function saveSettings() {
  toast('Settings saved','success');
}

/* ══════════ UTILS ══════════ */
function v(id){const el=document.getElementById(id);return el?el.value:'';}
function setV(id,val){const el=document.getElementById(id);if(el&&val!=null)el.value=val;}
function esc(s){if(!s)return'';const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function togglePassword(id,btn){const inp=document.getElementById(id);const h=inp.type==='password';inp.type=h?'text':'password';btn.innerHTML=`<i class="fa-solid fa-eye${h?'-slash':''}"></i>`;}
function toast(msg,type='info'){
  const c=document.getElementById('toast-container');
  const icons={success:'fa-circle-check',error:'fa-circle-xmark',info:'fa-circle-info'};
  const t=document.createElement('div');t.className=`toast ${type}`;
  t.innerHTML=`<i class="fa-solid ${icons[type]||icons.info}"></i><span>${esc(msg)}</span>`;
  c.appendChild(t);setTimeout(()=>{t.classList.add('toast-exit');setTimeout(()=>t.remove(),300);},3500);
}

/* ══════════ INIT ══════════ */
// Firebase handles auto-login via onAuthStateChanged above
