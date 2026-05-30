// NeuroStudy - Main Frontend Application

// ============================================================
// Global State
// ============================================================
let subjects = [];
let calendar = null;
let allQuotes = [];
let currentScheduleType = 'weekly';

// ============================================================
// Initialize Application
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    await loadQuotes();
    await loadSubjects();
    await loadPreferences();
    initChatbot();
    initCalendar();
    updateDashboard();
    setGreeting();
});

function setGreeting() {
    const hour = new Date().getHours();
    const greeting = hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : hour < 21 ? 'Evening' : 'Night';
    document.getElementById('greeting-text').textContent = greeting;
}

// ============================================================
// Toast Notifications
// ============================================================
function showToast(message, type = 'info', duration = 4000) {
    const icons = { info: 'ℹ️', success: '✅', warning: '⚠️', error: '❌', milestone: '🏆' };
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span class="text-xl">${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

// ============================================================
// Quotes System
// ============================================================
async function loadQuotes() {
    try {
        const response = await fetch('/static/data/quotes.json');
        allQuotes = await response.json();
        updateQuoteOfDay();
    } catch (e) {
        console.error('Failed to load quotes', e);
    }
}

function updateQuoteOfDay() {
    const today = new Date().toDateString();
    let qotd = localStorage.getItem('qotd');
    if (qotd) {
        qotd = JSON.parse(qotd);
        if (qotd.date === today) {
            document.getElementById('qotd-text').textContent = qotd.quote.text;
            document.getElementById('qotd-author').textContent = `— ${qotd.quote.author}`;
            return;
        }
    }
    const randomQuote = allQuotes[Math.floor(Math.random() * allQuotes.length)];
    localStorage.setItem('qotd', JSON.stringify({ date: today, quote: randomQuote }));
    document.getElementById('qotd-text').textContent = randomQuote.text;
    document.getElementById('qotd-author').textContent = `— ${randomQuote.author}`;
}

// ============================================================
// Subjects Management
// ============================================================
async function loadSubjects() {
    const response = await fetch('/api/subjects');
    subjects = await response.json();
    renderSubjectsGrid();
    renderSubjectsSelect();
    updateDashboardStats();
}

function renderSubjectsGrid() {
    const container = document.getElementById('subjects-grid');
    if (!subjects.length) {
        container.innerHTML = `<div class="col-span-full text-center py-12 text-gray-400">📚 No subjects yet. Click "Add Subject" to get started.</div>`;
        return;
    }
    
    container.innerHTML = subjects.map(subj => `
        <div class="card fade-in">
            <div class="flex items-start justify-between mb-3">
                <div>
                    <h3 class="font-semibold text-lg">${escapeHtml(subj.name)}</h3>
                    <div class="flex gap-2 mt-1">
                        <span class="badge badge-${subj.type}">${getTypeIcon(subj.type)} ${subj.type}</span>
                        ${subj.days_left <= 3 && subj.difficulty >= 7 ? '<span class="badge" style="background:rgba(239,68,68,0.2);color:#ef4444">🔴 URGENT</span>' : ''}
                        ${subj.is_weak ? '<span class="badge" style="background:rgba(245,158,11,0.2);color:#fbbf24">⚠️ Weak Subject</span>' : ''}
                    </div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold" style="color:${getDifficultyColor(subj.difficulty)}">${subj.difficulty}</div>
                    <div class="text-xs text-gray-400">difficulty</div>
                </div>
            </div>
            
            <div class="space-y-2 mb-4">
                <div class="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>${subj.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${subj.progress}%"></div>
                </div>
                <div class="flex justify-between text-sm text-gray-400">
                    <span>📚 ${subj.completed_hours}h / ${subj.estimated_hours}h</span>
                    <span>📅 ${subj.days_left === 999 ? 'No deadline' : subj.days_left + ' days left'}</span>
                </div>
            </div>
            
            <div class="flex gap-2">
                <button class="btn btn-primary text-sm flex-1" onclick="openSessionModal(${subj.id})">📝 Log Session</button>
                <button class="btn btn-secondary text-sm" onclick="toggleWeakSubject(${subj.id})">${subj.is_weak ? '✓ Mark Strong' : '⚠️ Mark Weak'}</button>
                <button class="btn btn-danger text-sm" onclick="deleteSubject(${subj.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

function getTypeIcon(type) {
    const icons = { coding: '💻', theory: '📚', math: '🔢', project: '🚀' };
    return icons[type] || '📘';
}

function getDifficultyColor(difficulty) {
    if (difficulty >= 8) return '#ef4444';
    if (difficulty >= 6) return '#f59e0b';
    if (difficulty >= 4) return '#4f46e5';
    return '#10b981';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function addSubject() {
    const name = document.getElementById('new-name').value.trim();
    if (!name) {
        showToast('Please enter a subject name', 'error');
        return;
    }
    
    const payload = {
        name: name,
        difficulty: parseFloat(document.getElementById('new-difficulty').value),
        estimated_hours: parseFloat(document.getElementById('new-hours').value),
        deadline: document.getElementById('new-deadline').value,
        type: document.getElementById('new-type').value
    };
    
    const response = await fetch('/api/subjects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (response.ok) {
        showToast(`Subject "${name}" added successfully!`, 'success');
        closeModal('add-subject-modal');
        await loadSubjects();
    }
}

async function deleteSubject(id) {
    if (!confirm('Delete this subject?')) return;
    await fetch(`/api/subjects/${id}`, { method: 'DELETE' });
    showToast('Subject deleted', 'info');
    await loadSubjects();
}

async function toggleWeakSubject(id) {
    const response = await fetch(`/api/subjects/${id}/weak`, { method: 'PUT' });
    if (response.ok) {
        await loadSubjects();
        showToast('Subject weakness status updated', 'success');
    }
}

// ============================================================
// Study Sessions
// ============================================================
function openSessionModal(subjectId) {
    document.getElementById('session-subject-id').value = subjectId;
    document.getElementById('session-modal').classList.remove('hidden');
}

async function logSession() {
    const subjectId = document.getElementById('session-subject-id').value;
    const hours = parseFloat(document.getElementById('session-hours').value);
    const notes = document.getElementById('session-notes').value;
    
    const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject_id: subjectId, actual_hours: hours, notes })
    });
    
    const data = await response.json();
    closeModal('session-modal');
    showToast(`Session logged! Cognitive load: ${data.cognitive_load}`, 'success');
    
    if (data.milestone) showToast(data.milestone, 'milestone');
    if (data.difficulty_message) showToast(data.difficulty_message, 'milestone');
    
    await loadSubjects();
    updateDashboard();
}

// ============================================================
// Schedule Generation (Daily/Weekly/Monthly)
// ============================================================
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        slotMinTime: '08:00:00',
        slotMaxTime: '22:00:00',
        height: 550,
        eventClick: function(info) {
            showToast(`${info.event.title} - ${info.event.extendedProps.type || 'Study'}`, 'info');
        }
    });
    calendar.render();
}

async function generateSchedule(type) {
    currentScheduleType = type;
    showToast(`🤖 AI generating ${type} schedule...`, 'info');
    
    const preferences = await getUserPreferences();
    const response = await fetch('/api/ai-schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_type: type, preferences })
    });
    
    const data = await response.json();
    displaySchedule(data);
}

function displaySchedule(scheduleData) {
    if (!calendar) initCalendar();
    calendar.removeAllEvents();
    
    if (scheduleData.duration_type === 'daily') {
        scheduleData.schedule.forEach(block => {
            if (block.subject !== 'BREAK') {
                calendar.addEvent({
                    title: block.subject,
                    start: formatDateTimeForCalendar(block.time, true),
                    end: formatDateTimeForCalendar(block.time, false, block.duration),
                    color: getSubjectColor(block.type),
                    extendedProps: { type: block.type, isWeak: block.is_weak }
                });
            }
        });
    } else if (scheduleData.duration_type === 'weekly') {
        scheduleData.schedule.forEach(day => {
            day.blocks.forEach(block => {
                if (block.subject !== 'BREAK') {
                    calendar.addEvent({
                        title: block.subject,
                        start: formatDateTimeForCalendar(block.time, true),
                        end: formatDateTimeForCalendar(block.time, false, block.duration),
                        color: getSubjectColor(block.type),
                        extendedProps: { type: block.type }
                    });
                }
            });
        });
    }
    
    showToast(`✅ ${scheduleData.duration_type} schedule generated!`, 'success');
}

function formatDateTimeForCalendar(timeStr, isStart, duration = null) {
    const today = new Date().toISOString().split('T')[0];
    if (timeStr.includes('-')) {
        const [start, end] = timeStr.split('-');
        if (isStart) return `${today}T${start}:00`;
        return `${today}T${end}:00`;
    }
    return `${today}T${timeStr}:00`;
}

function getSubjectColor(type) {
    const colors = { coding: '#4f46e5', theory: '#0ea5e9', math: '#f59e0b', project: '#10b981' };
    return colors[type] || '#6b7280';
}

// ============================================================
// User Preferences (Free Time, Study Duration)
// ============================================================
async function getUserPreferences() {
    const response = await fetch('/api/preferences');
    return await response.json();
}

async function savePreferences() {
    const preferences = {
        free_time: {
            monday: getTimeSlots('monday'),
            tuesday: getTimeSlots('tuesday'),
            wednesday: getTimeSlots('wednesday'),
            thursday: getTimeSlots('thursday'),
            friday: getTimeSlots('friday'),
            saturday: getTimeSlots('saturday'),
            sunday: getTimeSlots('sunday')
        },
        break_duration: parseInt(document.getElementById('break-duration').value),
        study_duration: parseFloat(document.getElementById('study-duration').value),
        preferred_format: document.getElementById('preferred-format').value
    };
    
    await fetch('/api/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences)
    });
    
    showToast('Preferences saved!', 'success');
    closeModal('preferences-modal');
}

function getTimeSlots(day) {
    const slots = [];
    const slotElements = document.querySelectorAll(`.time-slot-${day}`);
    slotElements.forEach(slot => {
        if (slot.value) slots.push(slot.value);
    });
    return slots;
}

async function loadPreferences() {
    const prefs = await getUserPreferences();
    if (prefs.free_time) {
        for (const [day, slots] of Object.entries(prefs.free_time)) {
            const container = document.getElementById(`free-time-${day}`);
            if (container && slots.length) {
                container.innerHTML = slots.map(slot => `<span class="badge">${slot}</span>`).join('');
            }
        }
    }
    document.getElementById('break-duration').value = prefs.break_duration || 15;
    document.getElementById('study-duration').value = prefs.study_duration || 2;
    document.getElementById('preferred-format').value = prefs.preferred_format || 'weekly';
}

// ============================================================
// Schedule Download (PDF/PNG/JSON)
// ============================================================
async function downloadSchedule(format) {
    if (format === 'json') {
        window.open('/api/export/json', '_blank');
        return;
    }
    
    const element = document.getElementById('calendar');
    if (!element) {
        showToast('Please generate a schedule first', 'warning');
        return;
    }
    
    if (format === 'png') {
        const canvas = await html2canvas(element, { scale: 2, backgroundColor: '#1e293b' });
        const link = document.createElement('a');
        link.download = `study_schedule_${currentScheduleType}.png`;
        link.href = canvas.toDataURL();
        link.click();
        showToast('Schedule downloaded as PNG!', 'success');
    } else if (format === 'pdf') {
        const { jsPDF } = window.jspdf;
        const canvas = await html2canvas(element, { scale: 2, backgroundColor: '#1e293b' });
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({ orientation: 'landscape', unit: 'px', format: [canvas.width, canvas.height] });
        pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save(`study_schedule_${currentScheduleType}.pdf`);
        showToast('Schedule downloaded as PDF!', 'success');
    }
}

// ============================================================
// Dashboard & Analytics
// ============================================================
async function updateDashboard() {
    const response = await fetch('/api/analytics');
    const data = await response.json();
    
    document.getElementById('stat-subjects').textContent = data.total_subjects;
    document.getElementById('stat-hours').textContent = data.total_hours + 'h';
    document.getElementById('stat-sessions').textContent = data.total_sessions;
    
    const avgProgress = data.subjects.length ? Math.round(data.subjects.reduce((a, b) => a + b.progress * 100, 0) / data.subjects.length) : 0;
    document.getElementById('stat-completion').textContent = avgProgress + '%';
    
    renderHeatmap(data.heatmap);
    updateBurnoutIndicator(data.burnout);
}

function renderHeatmap(heatmapData) {
    const container = document.getElementById('heatmap-container');
    if (!container) return;
    
    const heatmap = {};
    heatmapData.forEach(h => heatmap[h.date] = h.hours);
    
    const today = new Date();
    let html = '';
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        const hours = heatmap[dateStr] || 0;
        const color = hours === 0 ? '#1e293b' : hours < 1 ? '#4f46e5' : hours < 2 ? '#7c3aed' : hours < 3 ? '#a78bfa' : '#c4b5fd';
        html += `<div class="heatmap-cell" style="background:${color}" title="${dateStr}: ${hours}h"></div>`;
    }
    container.innerHTML = html;
}

function updateBurnoutIndicator(burnout) {
    const el = document.getElementById('burnout-status');
    if (!el) return;
    
    if (burnout.level === 'critical') {
        el.innerHTML = `🔴 Critical Burnout Risk - ${burnout.suggestion}`;
        el.className = 'text-red-400 text-sm';
    } else if (burnout.level === 'warning') {
        el.innerHTML = `⚠️ Warning - ${burnout.suggestion}`;
        el.className = 'text-amber-400 text-sm';
    } else {
        el.innerHTML = `✅ Healthy - ${burnout.suggestion}`;
        el.className = 'text-green-400 text-sm';
    }
}

// ============================================================
// AI Chatbot
// ============================================================
let chatbotOpen = false;

function initChatbot() {
    const toggle = document.getElementById('chatbot-toggle');
    if (toggle) {
        toggle.addEventListener('click', toggleChatbot);
    }
}

function toggleChatbot() {
    chatbotOpen = !chatbotOpen;
    const window = document.getElementById('chatbot-window');
    if (window) {
        window.style.display = chatbotOpen ? 'flex' : 'none';
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;
    
    addChatMessage(query, 'user');
    input.value = '';
    
    showToast('🤖 AI is thinking...', 'info', 1000);
    
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    
    const data = await response.json();
    addChatMessage(data.response, 'bot');
}

function addChatMessage(message, sender) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chatbot-message ${sender}`;
    div.textContent = message;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// ============================================================
// Utility Functions
// ============================================================
function renderSubjectsSelect() {
    const selects = ['prereq-source', 'prereq-target'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = subjects.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join('');
        }
    });
}

function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section-${sectionId}`).classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(n => {
        if (n.textContent.toLowerCase().includes(sectionId)) n.classList.add('active');
    });
}

// ============================================================
// LeetCode Practice
// ============================================================
async function fetchLeetCode() {
    const topic = document.getElementById('leetcode-topic').value || 'default';
    const response = await fetch(`/api/leetcode?topic=${encodeURIComponent(topic)}`);
    const problems = await response.json();
    
    const container = document.getElementById('leetcode-results');
    container.innerHTML = problems.map(p => `
        <div class="card">
            <h3 class="font-semibold">${p.title}</h3>
            <span class="badge ${p.difficulty === 'Easy' ? 'text-green-400' : p.difficulty === 'Hard' ? 'text-red-400' : 'text-amber-400'}">${p.difficulty}</span>
            <a href="${p.url}" target="_blank" class="btn btn-primary text-sm mt-3 block text-center">Solve on LeetCode</a>
        </div>
    `).join('');
}