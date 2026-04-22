import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
const TOKEN_KEY = 'mindful_token'
const PROFILE_KEY = 'mindful_profile'

const emptyAuth = {
  email: '',
  password: '',
  full_name: '',
}

const emptyCircle = {
  name: '',
  description: '',
  is_anonymous: false,
}

function getStoredProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY)) || null
  } catch {
    return null
  }
}

function initials(nameOrEmail = '') {
  const clean = nameOrEmail.trim()
  if (!clean) return 'MC'
  const words = clean.includes('@') ? clean.split('@')[0].split(/[._-]/) : clean.split(' ')
  return words
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('')
}

function formatDate(value) {
  if (!value) return 'No date'
  const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value)
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')
  const [profile, setProfile] = useState(() => getStoredProfile())
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState(emptyAuth)
  const [authLoading, setAuthLoading] = useState(false)

  const [view, setView] = useState('dashboard')
  const [circles, setCircles] = useState([])
  const [selectedCircle, setSelectedCircle] = useState(null)
  const [members, setMembers] = useState([])
  const [questions, setQuestions] = useState([])
  const [todayQuestion, setTodayQuestion] = useState(null)
  const [selectedQuestion, setSelectedQuestion] = useState(null)
  const [answers, setAnswers] = useState([])
  const [answerText, setAnswerText] = useState('')
  const [todayQuestionText, setTodayQuestionText] = useState('')
  const [circleNotice, setCircleNotice] = useState('')
  const [circleForm, setCircleForm] = useState(emptyCircle)
  const [joinForm, setJoinForm] = useState({ circleId: '', displayName: '' })
  const [isCreatingCircle, setIsCreatingCircle] = useState(false)
  const [isJoiningCircle, setIsJoiningCircle] = useState(false)
  const [isSavingQuestion, setIsSavingQuestion] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    })

    if (response.status === 204) return null

    const contentType = response.headers.get('content-type') || ''
    const raw = await response.text()
    let payload = null
    if (contentType.includes('application/json') && raw) {
      try {
        payload = JSON.parse(raw)
      } catch {
        payload = null
      }
    }

    if (!response.ok) {
      throw new Error(payload?.detail || raw || response.statusText || 'Request failed')
    }

    return payload
  }

  function showMessage(text) {
    setMessage(text)
    window.setTimeout(() => setMessage(''), 2400)
  }

  function showError(text) {
    setError(text)
    window.setTimeout(() => setError(''), 4200)
  }

  async function loadCircles() {
    if (!token) return
    setIsLoading(true)
    try {
      const data = await request('/circles')
      setCircles(data)
      if (selectedCircle) {
        const fresh = data.find((circle) => circle.id === selectedCircle.id)
        setSelectedCircle(fresh || null)
      }
    } catch (err) {
      showError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  async function loadCircleDetails(circle) {
    setSelectedCircle(circle)
    setView('circle')
    setCircleNotice('')
    setTodayQuestion(null)
    setTodayQuestionText('')
    setSelectedQuestion(null)
    setAnswers([])
    setAnswerText('')
    setIsLoading(true)

    const [memberResult, questionResult, todayResult] = await Promise.allSettled([
      request(`/circles/${circle.id}/members`),
      request(`/circles/${circle.id}/questions`),
      request(`/circles/${circle.id}/questions/today`),
    ])

    if (memberResult.status === 'fulfilled') {
      setMembers(memberResult.value)
    } else {
      setMembers([])
      showError(`Members: ${memberResult.reason.message}`)
    }

    const notices = []

    if (questionResult.status === 'fulfilled') {
      setQuestions(questionResult.value)
    } else {
      setQuestions([])
      notices.push(`Questions: ${questionResult.reason.message}`)
    }

    if (todayResult.status === 'fulfilled') {
      setTodayQuestion(todayResult.value)
      setTodayQuestionText(todayResult.value.text)
      setQuestions((current) => {
        const exists = current.some((question) => question.id === todayResult.value.id)
        return exists ? current : [todayResult.value, ...current]
      })
    } else {
      notices.push(`Today: ${todayResult.reason.message}`)
    }

    setCircleNotice(notices.join(' '))
    setIsLoading(false)
  }

  function selectQuestion(question) {
    setSelectedQuestion(question)
    setAnswers([])
    setAnswerText('')
  }

  async function loadAnswers(question) {
    selectQuestion(question)
    setIsLoading(true)

    try {
      const data = await request(`/questions/${question.id}/answers`)
      setAnswers(data)
    } catch (err) {
      showError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleAuth(event) {
    event.preventDefault()
    setAuthLoading(true)
    setError('')

    const body =
      authMode === 'signup'
        ? authForm
        : { email: authForm.email, password: authForm.password }

    try {
      const data = await fetch(`${API_BASE}/auth/${authMode === 'signup' ? 'register' : 'login'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const payload = await data.json()
      if (!data.ok) throw new Error(payload?.detail || 'Authentication failed')

      localStorage.setItem(TOKEN_KEY, payload.access_token)
      const nextProfile = {
        email: authForm.email,
        full_name: authMode === 'signup' ? authForm.full_name : authForm.email,
      }
      localStorage.setItem(PROFILE_KEY, JSON.stringify(nextProfile))
      setToken(payload.access_token)
      setProfile(nextProfile)
      setAuthForm(emptyAuth)
      showMessage(authMode === 'signup' ? 'Account created.' : 'Signed in.')
    } catch (err) {
      showError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(PROFILE_KEY)
    setToken('')
    setProfile(null)
    setCircles([])
    setSelectedCircle(null)
    setView('dashboard')
  }

  async function createCircle(event) {
    event.preventDefault()
    if (!circleForm.name.trim()) {
      showError('Circle name is required.')
      return
    }

    setIsCreatingCircle(true)
    try {
      const circle = await request('/circles', {
        method: 'POST',
        body: JSON.stringify({
          name: circleForm.name.trim(),
          description: circleForm.description.trim() || null,
          is_anonymous: circleForm.is_anonymous,
        }),
      })
      setCircleForm(emptyCircle)
      setCircles((current) => [circle, ...current])
      showMessage('Circle created.')
    } catch (err) {
      showError(err.message)
    } finally {
      setIsCreatingCircle(false)
    }
  }

  async function joinCircle(event) {
    event.preventDefault()
    const circleId = Number(joinForm.circleId)
    if (!circleId || !joinForm.displayName.trim()) {
      showError('Circle ID and display name are required.')
      return
    }

    setIsJoiningCircle(true)
    try {
      await request(`/circles/${circleId}/join`, {
        method: 'POST',
        body: JSON.stringify({ display_name: joinForm.displayName.trim() }),
      })
      setJoinForm({ circleId: '', displayName: '' })
      await loadCircles()
      showMessage('Joined circle.')
    } catch (err) {
      showError(err.message)
    } finally {
      setIsJoiningCircle(false)
    }
  }

  async function submitAnswer(event) {
    event.preventDefault()
    if (!selectedQuestion || !answerText.trim()) {
      showError('Choose a question and write an answer first.')
      return
    }

    try {
      await request(`/questions/${selectedQuestion.id}/answers`, {
        method: 'POST',
        body: JSON.stringify({ text: answerText.trim() }),
      })
      setAnswerText('')
      await loadAnswers(selectedQuestion)
      showMessage('Answer submitted.')
    } catch (err) {
      showError(err.message)
    }
  }

  async function saveTodayQuestion(event) {
    event.preventDefault()
    if (!selectedCircle || !todayQuestionText.trim()) {
      showError('Question text is required.')
      return
    }

    setIsSavingQuestion(true)
    try {
      const question = await request(`/circles/${selectedCircle.id}/questions/today`, {
        method: 'PATCH',
        body: JSON.stringify({ text: todayQuestionText.trim() }),
      })
      setTodayQuestion(question)
      setSelectedQuestion(question)
      setQuestions((current) => {
        const exists = current.some((item) => item.id === question.id)
        return exists ? current.map((item) => (item.id === question.id ? question : item)) : [question, ...current]
      })
      showMessage("Today's question was saved.")
    } catch (err) {
      showError(err.message)
    } finally {
      setIsSavingQuestion(false)
    }
  }

  useEffect(() => {
    if (!token) return

    let isActive = true

    async function loadInitialCircles() {
      setIsLoading(true)
      try {
        const response = await fetch(`${API_BASE}/circles`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const raw = await response.text()
        let payload = null
        try {
          payload = raw ? JSON.parse(raw) : null
        } catch {
          payload = null
        }
        if (!response.ok) throw new Error(payload?.detail || raw || response.statusText || 'Request failed')
        if (isActive) setCircles(payload)
      } catch (err) {
        if (isActive) {
          setError(err.message)
          window.setTimeout(() => setError(''), 4200)
        }
      } finally {
        if (isActive) setIsLoading(false)
      }
    }

    loadInitialCircles()

    return () => {
      isActive = false
    }
  }, [token])

  if (!token) {
    return (
      <main className="auth-shell">
        <section className="auth-card">
          <div className="brand-lockup">
            <img src="/mindful_circle_logo.png" alt="Mindful Circle" />
            <div>
              <p className="eyebrow">Mindful Circles</p>
              <h1>{authMode === 'signup' ? 'Create your space.' : 'Welcome back.'}</h1>
            </div>
          </div>

          <form className="auth-form" onSubmit={handleAuth}>
            <div className="segmented" aria-label="Authentication mode">
              <button
                className={authMode === 'login' ? 'active' : ''}
                type="button"
                onClick={() => setAuthMode('login')}
              >
                Login
              </button>
              <button
                className={authMode === 'signup' ? 'active' : ''}
                type="button"
                onClick={() => setAuthMode('signup')}
              >
                Sign up
              </button>
            </div>

            {authMode === 'signup' && (
              <label>
                Full name
                <input
                  value={authForm.full_name}
                  onChange={(event) => setAuthForm({ ...authForm, full_name: event.target.value })}
                  required
                  autoComplete="name"
                />
              </label>
            )}

            <label>
              Email
              <input
                type="email"
                value={authForm.email}
                onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })}
                required
                autoComplete="email"
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={authForm.password}
                onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                required
                autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'}
              />
            </label>

            <button className="primary" disabled={authLoading} type="submit">
              {authLoading ? 'Please wait...' : authMode === 'signup' ? 'Create account' : 'Login'}
            </button>
          </form>
        </section>
        <Toast message={message} error={error} />
      </main>
    )
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <button className="brand-button" type="button" onClick={() => setView('dashboard')}>
          <img src="/mindful_circle_logo.png" alt="Mindful Circle" />
        </button>

        <nav className="nav-list" aria-label="Main">
          <button
            className={view === 'dashboard' ? 'active' : ''}
            type="button"
            onClick={() => setView('dashboard')}
          >
            <Icon name="home" />
            Dashboard
          </button>
          {selectedCircle && (
            <button
              className={view === 'circle' ? 'active' : ''}
              type="button"
              onClick={() => setView('circle')}
            >
              <Icon name="circle" />
              Circle page
            </button>
          )}
        </nav>

        <div className="profile-card">
          <span className="avatar">{initials(profile?.full_name || profile?.email)}</span>
          <div>
            <strong>{profile?.full_name || 'Mindful member'}</strong>
            <span>{profile?.email}</span>
          </div>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">{view === 'circle' ? 'Circle' : 'Dashboard'}</p>
            <h1>{view === 'circle' && selectedCircle ? selectedCircle.name : 'Your mindful circles'}</h1>
          </div>
          <button className="secondary" type="button" onClick={logout}>
            <Icon name="logout" />
            Logout
          </button>
        </header>

        {view === 'dashboard' ? (
          <Dashboard
            circles={circles}
            circleForm={circleForm}
            joinForm={joinForm}
            isCreatingCircle={isCreatingCircle}
            isJoiningCircle={isJoiningCircle}
            isLoading={isLoading}
            onCircleForm={setCircleForm}
            onJoinForm={setJoinForm}
            onCreateCircle={createCircle}
            onJoinCircle={joinCircle}
            onOpenCircle={loadCircleDetails}
          />
        ) : (
          <CirclePage
            circle={selectedCircle}
            profile={profile}
            members={members}
            questions={questions}
            todayQuestion={todayQuestion}
            selectedQuestion={selectedQuestion}
            answers={answers}
            answerText={answerText}
            todayQuestionText={todayQuestionText}
            isLoading={isLoading}
            isSavingQuestion={isSavingQuestion}
            notice={circleNotice}
            onBack={() => setView('dashboard')}
            onSelectQuestion={selectQuestion}
            onPickQuestion={loadAnswers}
            onAnswerText={setAnswerText}
            onTodayQuestionText={setTodayQuestionText}
            onSaveTodayQuestion={saveTodayQuestion}
            onSubmitAnswer={submitAnswer}
          />
        )}
      </section>

      <Toast message={message} error={error} />
    </main>
  )
}

function Dashboard({
  circles,
  circleForm,
  joinForm,
  isCreatingCircle,
  isJoiningCircle,
  isLoading,
  onCircleForm,
  onJoinForm,
  onCreateCircle,
  onJoinCircle,
  onOpenCircle,
}) {
  return (
    <div className="dashboard-grid">
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Circles</h2>
            <p>{circles.length ? `${circles.length} circle${circles.length === 1 ? '' : 's'}` : 'No circles yet'}</p>
          </div>
          {isLoading && <span className="status-pill">Loading</span>}
        </div>

        <div className="circle-list">
          {circles.map((circle) => (
            <button className="circle-row" key={circle.id} type="button" onClick={() => onOpenCircle(circle)}>
              <span className="avatar">{initials(circle.name)}</span>
              <span>
                <strong>{circle.name}</strong>
                <small>Circle ID {circle.id} - {circle.description || 'No description'}</small>
              </span>
              <span className="status-pill">{circle.is_anonymous ? 'Anonymous' : 'Named'}</span>
            </button>
          ))}

          {!circles.length && (
            <div className="empty-state">
              <Icon name="circle" />
              <h3>Create or join a circle</h3>
              <p>Your groups will appear here after the API returns them.</p>
            </div>
          )}
        </div>
      </section>

      <aside className="form-stack">
        <section className="panel">
          <h2>Create circle</h2>
          <form className="stack-form" onSubmit={onCreateCircle}>
            <label>
              Name
              <input
                value={circleForm.name}
                onChange={(event) => onCircleForm({ ...circleForm, name: event.target.value })}
                required
              />
            </label>
            <label>
              Description
              <textarea
                value={circleForm.description}
                onChange={(event) => onCircleForm({ ...circleForm, description: event.target.value })}
                rows="3"
              />
            </label>
            <label className="check-row">
              <input
                type="checkbox"
                checked={circleForm.is_anonymous}
                onChange={(event) => onCircleForm({ ...circleForm, is_anonymous: event.target.checked })}
              />
              Anonymous answers
            </label>
            <button className="primary" disabled={isCreatingCircle} type="submit">
              <Icon name="plus" />
              {isCreatingCircle ? 'Creating...' : 'Create'}
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>Join circle</h2>
          <form className="stack-form" onSubmit={onJoinCircle}>
            <label>
              Circle ID
              <input
                inputMode="numeric"
                value={joinForm.circleId}
                onChange={(event) => onJoinForm({ ...joinForm, circleId: event.target.value })}
                required
              />
            </label>
            <label>
              Display name
              <input
                value={joinForm.displayName}
                onChange={(event) => onJoinForm({ ...joinForm, displayName: event.target.value })}
                required
              />
            </label>
            <button className="secondary" disabled={isJoiningCircle} type="submit">
              <Icon name="enter" />
              {isJoiningCircle ? 'Joining...' : 'Join'}
            </button>
          </form>
        </section>
      </aside>
    </div>
  )
}

function CirclePage({
  circle,
  profile,
  members,
  questions,
  todayQuestion,
  selectedQuestion,
  answers,
  answerText,
  todayQuestionText,
  isLoading,
  isSavingQuestion,
  notice,
  onBack,
  onSelectQuestion,
  onPickQuestion,
  onAnswerText,
  onTodayQuestionText,
  onSaveTodayQuestion,
  onSubmitAnswer,
}) {
  if (!circle) {
    return (
      <section className="panel">
        <div className="empty-state">
          <h2>No circle selected</h2>
          <button className="primary" type="button" onClick={onBack}>
            Back to dashboard
          </button>
        </div>
      </section>
    )
  }

  const todayTurnName = todayQuestion?.asked_member_display_name || 'a member'
  const profileName = profile?.full_name || ''
  const profileEmailName = profile?.email?.split('@')[0] || ''
  const isYourTurn =
    members.length === 1 ||
    todayTurnName === profileName ||
    todayTurnName === profile?.email ||
    todayTurnName === profileEmailName

  return (
    <div className="circle-grid">
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Questions</h2>
            <p>{circle.description || `Circle ID ${circle.id}`}</p>
          </div>
          <span className="status-pill">{circle.is_anonymous ? 'Anonymous' : 'Named'}</span>
        </div>

        {notice && <p className="notice">{notice}</p>}

        <div className="today-card">
          <span className="status-pill">{isYourTurn ? "It's your turn to ask" : `${todayTurnName}'s turn to ask`}</span>
          <h3>{todayQuestion?.text || 'No question for today yet'}</h3>
          <p>
            {todayQuestion
              ? 'Ask the circle question for today, then answer it yourself before viewing the responses.'
              : 'The backend creates a daily question for the circle. Restart the backend or wait for the scheduler if this stays empty.'}
          </p>
          {todayQuestion && isYourTurn && (
            <form className="ask-form" onSubmit={onSaveTodayQuestion}>
              <label>
                Today's question
                <textarea
                  value={todayQuestionText}
                  onChange={(event) => onTodayQuestionText(event.target.value)}
                  rows="3"
                  placeholder="Ask the question for your circle..."
                />
              </label>
              <button className="secondary" disabled={isSavingQuestion} type="submit">
                <Icon name="send" />
                {isSavingQuestion ? 'Saving...' : 'Save question'}
              </button>
            </form>
          )}
          {todayQuestion && (
            <button className="secondary" type="button" onClick={() => onSelectQuestion(todayQuestion)}>
              <Icon name="question" />
              Answer this question
            </button>
          )}
        </div>

        <div className="question-list">
          {questions.map((question) => (
            <button
              className={`question-row ${selectedQuestion?.id === question.id ? 'active' : ''}`}
              key={question.id}
              type="button"
              onClick={() => onPickQuestion(question)}
            >
              <span>{question.text}</span>
              <small>
                {formatDate(question.asked_date)}
                {question.asked_member_display_name ? ` for ${question.asked_member_display_name}` : ''}
              </small>
            </button>
          ))}

          {!questions.length && (
            <div className="empty-state">
              <Icon name="question" />
              <h3>No questions yet</h3>
              <p>The backend scheduler creates daily questions for each circle.</p>
            </div>
          )}
        </div>
      </section>

      <section className="panel answer-panel">
        <div className="panel-head">
          <div>
            <h2>Answers</h2>
            <p>{selectedQuestion ? selectedQuestion.text : 'Select a question'}</p>
          </div>
          {isLoading && <span className="status-pill">Loading</span>}
        </div>

        {selectedQuestion && (
          <form className="answer-form" onSubmit={onSubmitAnswer}>
            <textarea
              value={answerText}
              onChange={(event) => onAnswerText(event.target.value)}
              rows="4"
              placeholder="Answer this question..."
            />
            <button className="primary" type="submit">
              <Icon name="send" />
              Submit answer
            </button>
          </form>
        )}

        <div className="answer-list">
          {answers.map((answer) => (
            <article className="answer-card" key={answer.id}>
              <div className="answer-meta">
                <span className="avatar">{initials(answer.display_name || 'A')}</span>
                <div>
                  <strong>{answer.display_name || 'Anonymous member'}</strong>
                  <small>{formatDate(answer.created_at)}</small>
                </div>
              </div>
              <p>{answer.text}</p>
            </article>
          ))}

          {selectedQuestion && !answers.length && (
            <div className="empty-state compact">
              <p>Answers appear here after you answer this question.</p>
            </div>
          )}
        </div>
      </section>

      <aside className="panel members-panel">
        <h2>Members</h2>
        <div className="member-list">
          {members.map((member) => (
            <div className="member-row" key={member.id}>
              <span className="avatar">{initials(member.display_name || `Member ${member.order + 1}`)}</span>
              <span>
                <strong>{member.display_name || `Member ${member.order + 1}`}</strong>
                <small>Joined {formatDate(member.joined_at)}</small>
              </span>
            </div>
          ))}
        </div>
      </aside>
    </div>
  )
}

function Toast({ message, error }) {
  const text = error || message
  if (!text) return null
  return <div className={`toast ${error ? 'error' : ''}`}>{text}</div>
}

function Icon({ name }) {
  const paths = {
    home: <path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-9.5Z" />,
    circle: <path d="M7 8a5 5 0 0 1 10 0c0 4-5 9-5 9S7 12 7 8Z" />,
    logout: <path d="M10 5H5v14h5M14 8l4 4-4 4M8 12h10" />,
    plus: <path d="M12 5v14M5 12h14" />,
    enter: <path d="M10 5h9v14h-9M14 8l4 4-4 4M4 12h14" />,
    question: <path d="M9.2 9a3 3 0 1 1 4.9 2.3c-1.1.8-2.1 1.4-2.1 2.7M12 18h.01" />,
    send: <path d="M4 12 20 4l-4 16-4-7-8-1Z" />,
  }

  return (
    <svg className="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        {paths[name]}
      </g>
    </svg>
  )
}

export default App
