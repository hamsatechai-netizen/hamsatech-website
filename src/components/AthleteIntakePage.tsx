import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  getPsychologyQuestions,
  submitAthleteIntake,
  type AthleteIntakePayload,
  type PsychologyQuestion,
} from '../lib/authApi'
import '../styles/AthleteIntake.css'
import CoachIntakePage from './CoachIntakePage'

const tabs = [
  { id: 'athlete', label: 'Athlete Master' },
  { id: 'family', label: 'Family Details' },
  { id: 'profile', label: 'Athlete Profile' },
  { id: 'session', label: 'Sessions Log' },
  { id: 'physiology', label: 'Physiology Data' },
  { id: 'psychology', label: 'Psychology' },
] as const

const INTAKE_DRAFT_PREFIX = 'hamsai-athlete-intake-draft:'
const INTAKE_TAB_PREFIX = 'hamsai-athlete-intake-tab:'

type TabId = (typeof tabs)[number]['id']
type TabStatus = 'pending' | 'partial' | 'complete'

function AthleteIntakePage() {
  const { user, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]['id']>('athlete')
  const [questions, setQuestions] = useState<PsychologyQuestion[]>([])
  const [questionError, setQuestionError] = useState('')
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false)
  const [submitState, setSubmitState] = useState({ loading: false, error: '', success: '' })
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [pendingModalTabs, setPendingModalTabs] = useState<string[]>([])
  const [form, setForm] = useState<AthleteIntakePayload>({
    athleteMaster: {
      name: '',
      age: 16,
      gender: 'Male',
      heightCm: 170,
      weightKg: 60,
      academyId: 'ACA-001',
      coachId: user?.assignedCoachEmail ?? '',
      contactNumber: '',
      email: user?.role === 'student' ? user.email : '',
    },
    familyDetails: {
      motherName: '',
      fatherName: '',
      motherOccupation: '',
      fatherOccupation: '',
      educationLevel: '',
      siblingDetails: '',
      familyConservative: 'No',
      disciplineLevel: '',
      healthConditions: '',
      fatherContactNumber: '',
      motherContactNumber: '',
      parentEmail: '',
      comments: '',
    },
    athleteProfile: {
      class: '',
      schoolName: '',
      dietType: 'Mixed',
      outsideFoodFrequency: 'Weekly',
      sleepTime: '22:00',
      wakeTime: '06:00',
      friendCircle: '',
      angerPattern: '',
      sadnessPattern: '',
      academicPerformance: '',
      reasonForShooting: '',
      athleteGoal: '',
    },
    sessionsLog: {
      coachId: user?.assignedCoachEmail ?? '',
      sessionDate: new Date().toISOString().slice(0, 10),
      startTime: '06:00',
      endTime: '07:30',
      trainingType: 'Shooting',
      location: '',
      notes: '',
    },
    physiologyData: {
      recordedDate: new Date().toISOString().slice(0, 10),
      restingHeartRate: 60,
      avgHeartRate: 110,
      spo2: 98,
      breathingRate: 16,
      sleepHours: 8,
      recoveryScore: 72,
      stressScore: 32,
      fatigueLevel: 4,
      remarks: '',
    },
    psychologyResponses: [],
  })

  const draftStorageKey = user?.email ? `${INTAKE_DRAFT_PREFIX}${user.email}` : null
  const tabStorageKey = user?.email ? `${INTAKE_TAB_PREFIX}${user.email}` : null

  const getGreeting = (fullName: string) => {
    const hour = new Date().getHours()
    const firstName = fullName.trim().split(/\s+/)[0] || fullName
    const salutation =
      hour < 12 ? 'good morning' : hour < 17 ? 'good afternoon' : 'good evening'
    return `Hey ${firstName}, ${salutation}.`
  }

  useEffect(() => {
    if (!draftStorageKey || typeof window === 'undefined') {
      return
    }

    const savedDraft = window.localStorage.getItem(draftStorageKey)
    if (!savedDraft) {
      return
    }

    try {
      const parsedDraft = JSON.parse(savedDraft) as AthleteIntakePayload
      setForm((current) => ({
        ...current,
        ...parsedDraft,
        athleteMaster: {
          ...current.athleteMaster,
          ...parsedDraft.athleteMaster,
          coachId: user?.assignedCoachEmail ?? parsedDraft.athleteMaster.coachId,
        },
        sessionsLog: {
          ...current.sessionsLog,
          ...parsedDraft.sessionsLog,
          coachId: user?.assignedCoachEmail ?? parsedDraft.sessionsLog.coachId,
        },
      }))
    } catch {
      window.localStorage.removeItem(draftStorageKey)
    }
  }, [draftStorageKey, user?.assignedCoachEmail, user?.email])

  useEffect(() => {
    if (!tabStorageKey || typeof window === 'undefined') {
      return
    }

    const savedTab = window.localStorage.getItem(tabStorageKey) as TabId | null
    if (savedTab && tabs.some((tab) => tab.id === savedTab)) {
      setActiveTab(savedTab)
    }
  }, [tabStorageKey])

  useEffect(() => {
    if (user?.email) {
      setForm((current) => ({
        ...current,
        athleteMaster: {
          ...current.athleteMaster,
          name: user.fullName,
          email: user.email,
          coachId: user.assignedCoachEmail ?? current.athleteMaster.coachId,
        },
        sessionsLog: {
          ...current.sessionsLog,
          coachId: user.assignedCoachEmail ?? current.sessionsLog.coachId,
        },
      }))
    }
  }, [user])

  useEffect(() => {
    if (!user) {
      return
    }

    const loadQuestions = async () => {
      setIsLoadingQuestions(true)
      setQuestionError('')
      try {
        const records = await getPsychologyQuestions()
        setQuestions(records)
        setForm((current) => ({
          ...current,
          psychologyResponses: records.map((question) => {
            const existingAnswer = current.psychologyResponses.find(
              (item) => item.questionId === question.questionId,
            )

            return {
              questionId: question.questionId,
              answerText: existingAnswer?.answerText ?? '',
              answerScore:
                existingAnswer?.answerScore ?? (question.questionType === 'Scale' ? 5 : undefined),
            }
          }),
        }))
      } catch (error) {
        setQuestionError(error instanceof Error ? error.message : 'Unable to load psychology questions')
      } finally {
        setIsLoadingQuestions(false)
      }
    }

    void loadQuestions()
  }, [user])

  useEffect(() => {
    if (!draftStorageKey || typeof window === 'undefined' || !user) {
      return
    }

    window.localStorage.setItem(draftStorageKey, JSON.stringify(form))
  }, [draftStorageKey, form, user])

  useEffect(() => {
    if (!tabStorageKey || typeof window === 'undefined' || !user) {
      return
    }

    window.localStorage.setItem(tabStorageKey, activeTab)
  }, [activeTab, tabStorageKey, user])

  const durationPreview = useMemo(() => {
    const start = new Date(`1970-01-01T${form.sessionsLog.startTime}:00`)
    const end = new Date(`1970-01-01T${form.sessionsLog.endTime}:00`)
    const minutes = Math.round((end.getTime() - start.getTime()) / 60000)
    return minutes > 0 ? minutes : 0
  }, [form.sessionsLog.endTime, form.sessionsLog.startTime])

  const psychologyReady = questions.length > 0 && form.psychologyResponses.length === questions.length

  const tabChecks: Record<TabId, boolean[]> = useMemo(
    () => ({
      athlete: [
        form.athleteMaster.name.trim().length >= 2,
        form.athleteMaster.age >= 5 && form.athleteMaster.age <= 80,
        form.athleteMaster.academyId.trim().length >= 1,
        form.athleteMaster.coachId.trim().length >= 1,
        form.athleteMaster.contactNumber.trim().length >= 7,
        /\S+@\S+\.\S+/.test(form.athleteMaster.email),
      ],
      family: [
        form.familyDetails.motherName.trim().length >= 2,
        form.familyDetails.fatherName.trim().length >= 2,
        form.familyDetails.motherOccupation.trim().length >= 2,
        form.familyDetails.fatherOccupation.trim().length >= 2,
        form.familyDetails.educationLevel.trim().length >= 2,
        form.familyDetails.siblingDetails.trim().length >= 2,
        form.familyDetails.disciplineLevel.trim().length >= 2,
        form.familyDetails.healthConditions.trim().length >= 2,
        form.familyDetails.fatherContactNumber.trim().length >= 7,
        form.familyDetails.motherContactNumber.trim().length >= 7,
        /\S+@\S+\.\S+/.test(form.familyDetails.parentEmail),
        form.familyDetails.comments.trim().length >= 2,
      ],
      profile: [
        form.athleteProfile.class.trim().length >= 1,
        form.athleteProfile.schoolName.trim().length >= 2,
        form.athleteProfile.friendCircle.trim().length >= 2,
        form.athleteProfile.angerPattern.trim().length >= 2,
        form.athleteProfile.sadnessPattern.trim().length >= 2,
        form.athleteProfile.academicPerformance.trim().length >= 2,
        form.athleteProfile.reasonForShooting.trim().length >= 2,
        form.athleteProfile.athleteGoal.trim().length >= 2,
      ],
      session: [
        form.sessionsLog.coachId.trim().length >= 1,
        form.sessionsLog.location.trim().length >= 2,
        form.sessionsLog.notes.trim().length >= 2,
        durationPreview > 0,
      ],
      physiology: [
        form.physiologyData.restingHeartRate >= 40 && form.physiologyData.restingHeartRate <= 200,
        form.physiologyData.avgHeartRate >= 40 && form.physiologyData.avgHeartRate <= 200,
        form.physiologyData.spo2 >= 80 && form.physiologyData.spo2 <= 100,
        form.physiologyData.sleepHours >= 0 && form.physiologyData.sleepHours <= 12,
        form.physiologyData.remarks.trim().length >= 2,
      ],
      psychology: psychologyReady
        ? form.psychologyResponses.map((item) => item.answerText.trim().length >= 2)
        : [false],
    }),
    [durationPreview, form, psychologyReady],
  )

  const tabStatusMap: Record<TabId, TabStatus> = useMemo(() => {
    const result = {} as Record<TabId, TabStatus>

    tabs.forEach((tab) => {
      const checks = tabChecks[tab.id]
      const completeCount = checks.filter(Boolean).length

      if (completeCount === 0) {
        result[tab.id] = 'pending'
      } else if (completeCount === checks.length) {
        result[tab.id] = 'complete'
      } else {
        result[tab.id] = 'partial'
      }
    })

    return result
  }, [tabChecks])

  const pendingTabs = useMemo(
    () => tabs.filter((tab) => tabStatusMap[tab.id] !== 'complete').map((tab) => tab.label),
    [tabStatusMap],
  )

  const completedTabCount = useMemo(
    () => tabs.filter((tab) => tabStatusMap[tab.id] === 'complete').length,
    [tabStatusMap],
  )

  const partialTabCount = useMemo(
    () => tabs.filter((tab) => tabStatusMap[tab.id] === 'partial').length,
    [tabStatusMap],
  )

  const tabFieldLabels: Record<TabId, Array<{ key: string; label: string; valid: boolean }>> = useMemo(
    () => ({
      athlete: [
        { key: 'athlete.name', label: 'Name', valid: form.athleteMaster.name.trim().length >= 2 },
        { key: 'athlete.age', label: 'Age', valid: form.athleteMaster.age >= 5 && form.athleteMaster.age <= 80 },
        { key: 'athlete.academyId', label: 'Academy ID', valid: form.athleteMaster.academyId.trim().length >= 1 },
        { key: 'athlete.coachId', label: 'Coach ID', valid: form.athleteMaster.coachId.trim().length >= 1 },
        { key: 'athlete.contact', label: 'Contact Number', valid: form.athleteMaster.contactNumber.trim().length >= 7 },
        { key: 'athlete.email', label: 'Email', valid: /\S+@\S+\.\S+/.test(form.athleteMaster.email) },
      ],
      family: [
        { key: 'family.motherName', label: 'Mother Name', valid: form.familyDetails.motherName.trim().length >= 2 },
        { key: 'family.fatherName', label: 'Father Name', valid: form.familyDetails.fatherName.trim().length >= 2 },
        { key: 'family.motherOccupation', label: 'Mother Occupation', valid: form.familyDetails.motherOccupation.trim().length >= 2 },
        { key: 'family.fatherOccupation', label: 'Father Occupation', valid: form.familyDetails.fatherOccupation.trim().length >= 2 },
        { key: 'family.educationLevel', label: 'Education Level', valid: form.familyDetails.educationLevel.trim().length >= 2 },
        { key: 'family.siblingDetails', label: 'Sibling Details', valid: form.familyDetails.siblingDetails.trim().length >= 2 },
        { key: 'family.disciplineLevel', label: 'Discipline Level', valid: form.familyDetails.disciplineLevel.trim().length >= 2 },
        { key: 'family.healthConditions', label: 'Health Conditions', valid: form.familyDetails.healthConditions.trim().length >= 2 },
        { key: 'family.fatherContact', label: 'Father Contact', valid: form.familyDetails.fatherContactNumber.trim().length >= 7 },
        { key: 'family.motherContact', label: 'Mother Contact', valid: form.familyDetails.motherContactNumber.trim().length >= 7 },
        { key: 'family.parentEmail', label: 'Parent Email', valid: /\S+@\S+\.\S+/.test(form.familyDetails.parentEmail) },
        { key: 'family.comments', label: 'Comments', valid: form.familyDetails.comments.trim().length >= 2 },
      ],
      profile: [
        { key: 'profile.class', label: 'Class', valid: form.athleteProfile.class.trim().length >= 1 },
        { key: 'profile.schoolName', label: 'School Name', valid: form.athleteProfile.schoolName.trim().length >= 2 },
        { key: 'profile.friendCircle', label: 'Friend Circle', valid: form.athleteProfile.friendCircle.trim().length >= 2 },
        { key: 'profile.angerPattern', label: 'Anger Pattern', valid: form.athleteProfile.angerPattern.trim().length >= 2 },
        { key: 'profile.sadnessPattern', label: 'Sadness Pattern', valid: form.athleteProfile.sadnessPattern.trim().length >= 2 },
        { key: 'profile.academicPerformance', label: 'Academic Performance', valid: form.athleteProfile.academicPerformance.trim().length >= 2 },
        { key: 'profile.reasonForShooting', label: 'Reason for Shooting', valid: form.athleteProfile.reasonForShooting.trim().length >= 2 },
        { key: 'profile.goal', label: 'Athlete Goal', valid: form.athleteProfile.athleteGoal.trim().length >= 2 },
      ],
      session: [
        { key: 'session.coachId', label: 'Coach ID', valid: form.sessionsLog.coachId.trim().length >= 1 },
        { key: 'session.location', label: 'Location', valid: form.sessionsLog.location.trim().length >= 2 },
        { key: 'session.notes', label: 'Notes', valid: form.sessionsLog.notes.trim().length >= 2 },
        { key: 'session.duration', label: 'Session Duration', valid: durationPreview > 0 },
      ],
      physiology: [
        { key: 'physiology.restingHeartRate', label: 'Resting Heart Rate', valid: form.physiologyData.restingHeartRate >= 40 && form.physiologyData.restingHeartRate <= 200 },
        { key: 'physiology.avgHeartRate', label: 'Average Heart Rate', valid: form.physiologyData.avgHeartRate >= 40 && form.physiologyData.avgHeartRate <= 200 },
        { key: 'physiology.spo2', label: 'SpO2', valid: form.physiologyData.spo2 >= 80 && form.physiologyData.spo2 <= 100 },
        { key: 'physiology.sleepHours', label: 'Sleep Hours', valid: form.physiologyData.sleepHours >= 0 && form.physiologyData.sleepHours <= 12 },
        { key: 'physiology.remarks', label: 'Remarks', valid: form.physiologyData.remarks.trim().length >= 2 },
      ],
      psychology: questions.map((question) => {
        const answer = form.psychologyResponses.find((item) => item.questionId === question.questionId)
        return {
          key: `psychology.${question.questionId}`,
          label: question.questionText,
          valid: (answer?.answerText ?? '').trim().length >= 2,
        }
      }),
    }),
    [durationPreview, form, questions],
  )

  const activeTabMissingFields = useMemo(
    () => tabFieldLabels[activeTab].filter((field) => !field.valid).map((field) => field.label),
    [activeTab, tabFieldLabels],
  )

  const persistDraft = (nextForm: AthleteIntakePayload) => {
    if (!draftStorageKey || typeof window === 'undefined') {
      return
    }

    window.localStorage.setItem(draftStorageKey, JSON.stringify(nextForm))
  }

  const scrollToFirstInvalidField = () => {
    window.setTimeout(() => {
      const target = document.querySelector<HTMLElement>(
        '.intake-card .intake-input-invalid, .intake-card input:invalid, .intake-card select:invalid, .intake-card textarea:invalid',
      )

      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' })
        if ('focus' in target) {
          target.focus()
        }
      }
    }, 120)
  }

  if (!isLoading && !user) {
    return <Navigate to="/signin" replace state={{ from: { pathname: '/athlete-intake' } }} />
  }

  if (!user) {
    return null
  }

  if (user.role === 'coach') {
    return <CoachIntakePage />
  }

  if (!user.assignedCoachEmail) {
    return (
      <section className="intake-shell">
        <div className="intake-container">
          <div className="intake-hero">
            <h1>{getGreeting(user.fullName)}</h1>
            <p>Your intake unlocks after a coach approves your assignment request.</p>
          </div>

          <div className="intake-card">
            <div className="dashboard-section-header">
              <h2>Coach approval needed</h2>
              <p>
                Request a coach code from your dashboard first. Once the coach approves your
                request, this intake will be ready for submission.
              </p>
            </div>
            <div className="dashboard-links">
              <Link to="/dashboard">Go to Dashboard</Link>
              <Link to="/profile">Open Profile</Link>
            </div>
          </div>
        </div>
      </section>
    )
  }

  const updateSection = <K extends keyof AthleteIntakePayload>(
    section: K,
    key: keyof AthleteIntakePayload[K],
    value: string | number,
  ) => {
    setForm((current) => {
      const nextForm = {
        ...current,
        [section]: {
          ...current[section],
          [key]: value,
        },
      }

      persistDraft(nextForm)
      return nextForm
    })
  }

  const updatePsychologyAnswer = (questionId: string, field: 'answerText' | 'answerScore', value: string | number) => {
    setForm((current) => {
      const nextForm = {
        ...current,
        psychologyResponses: current.psychologyResponses.map((item) =>
          item.questionId === questionId ? { ...item, [field]: value } : item,
        ),
      }

      persistDraft(nextForm)
      return nextForm
    })
  }

  const markTouched = (field: string) => {
    setTouched((current) => ({ ...current, [field]: true }))
  }

  const markFieldsTouched = (fields: string[]) => {
    setTouched((current) => ({
      ...current,
      ...Object.fromEntries(fields.map((field) => [field, true])),
    }))
  }

  const getTextFeedback = (
    value: string,
    options: {
      field: string
      required?: boolean
      minLength?: number
      maxLength?: number
      caseSensitive?: boolean
      helper?: string
    },
  ) => {
    const isTouched = touched[options.field]
    const trimmed = value.trim()

    if (options.required && isTouched && trimmed.length === 0) {
      return { tone: 'error', text: 'This field is mandatory.' }
    }

    if (options.minLength && trimmed.length > 0 && trimmed.length < options.minLength) {
      return { tone: 'error', text: `Use at least ${options.minLength} characters.` }
    }

    if (options.maxLength) {
      const remaining = options.maxLength - value.length
      if (remaining < 0) {
        return { tone: 'error', text: `Keep this within ${options.maxLength} characters.` }
      }

      if (remaining <= 12) {
        return { tone: 'info', text: `${remaining} characters remaining.` }
      }
    }

    if (options.caseSensitive) {
      return { tone: 'info', text: `${options.helper ?? 'Case-sensitive. Use the exact stored code.'}` }
    }

    if (options.helper) {
      return { tone: 'info', text: options.helper }
    }

    return null
  }

  const isInvalidTextField = (
    value: string,
    options: { field: string; required?: boolean; minLength?: number; maxLength?: number },
  ) => {
    const isTouched = touched[options.field]
    if (!isTouched) {
      return false
    }

    const trimmed = value.trim()
    if (options.required && trimmed.length === 0) {
      return true
    }
    if (options.minLength && trimmed.length > 0 && trimmed.length < options.minLength) {
      return true
    }
    if (options.maxLength && value.length > options.maxLength) {
      return true
    }
    return false
  }

  const isInvalidNumberField = (value: number, options: { min: number; max: number; field: string }) => {
    if (!touched[options.field]) {
      return false
    }
    return Number.isNaN(value) || value < options.min || value > options.max
  }

  const getRangeFeedback = (
    value: number,
    options: { min: number; max: number; helper?: string },
  ) => {
    if (Number.isNaN(value)) {
      return { tone: 'error', text: 'Enter a valid number.' }
    }

    if (value < options.min || value > options.max) {
      return { tone: 'error', text: `Use a value between ${options.min} and ${options.max}.` }
    }

    return { tone: 'info', text: options.helper ?? `Allowed range: ${options.min}-${options.max}.` }
  }

  const configError = submitState.error.includes('Supabase is not configured')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (pendingTabs.length > 0) {
      const firstPendingTab = tabs.find((tab) => tabStatusMap[tab.id] !== 'complete')
      markFieldsTouched(
        tabs
          .filter((tab) => tabStatusMap[tab.id] !== 'complete')
          .flatMap((tab) => tabFieldLabels[tab.id].filter((field) => !field.valid).map((field) => field.key)),
      )
      if (firstPendingTab) {
        setActiveTab(firstPendingTab.id)
      }

      const tabSummary = pendingTabs.join(', ')
      setSubmitState({
        loading: false,
        error: `Complete these tabs before submitting: ${tabSummary}.`,
        success: '',
      })
      setPendingModalTabs(pendingTabs)
      scrollToFirstInvalidField()
      return
    }

    setSubmitState({ loading: true, error: '', success: '' })
    try {
      const result = await submitAthleteIntake(form)
      if (draftStorageKey && typeof window !== 'undefined') {
        window.localStorage.removeItem(draftStorageKey)
      }
      if (tabStorageKey && typeof window !== 'undefined') {
        window.localStorage.removeItem(tabStorageKey)
      }
      setSubmitState({
        loading: false,
        error: '',
        success: `Athlete record saved. Athlete ID: ${result.athleteId}`,
      })
    } catch (error) {
      setSubmitState({
        loading: false,
        error: error instanceof Error ? error.message : 'Unable to submit athlete intake',
        success: '',
      })
    }
  }

  return (
    <section className="intake-shell">
      <div className="intake-container">
        <div className="intake-hero">
          <h1>{getGreeting(user.fullName)}</h1>
          <p>
            Let’s capture today’s intake clearly so your coach can review the right signals without extra back-and-forth.
          </p>
          <div className="intake-progress-strip">
            <article className="intake-progress-card">
              <span>Completed</span>
              <strong>{completedTabCount}</strong>
            </article>
            <article className="intake-progress-card intake-progress-card-warn">
              <span>In Progress</span>
              <strong>{partialTabCount}</strong>
            </article>
            <article className="intake-progress-card intake-progress-card-danger">
              <span>Pending</span>
              <strong>{tabs.length - completedTabCount - partialTabCount}</strong>
            </article>
          </div>
        </div>

        {configError ? (
          <div className="intake-config-warning">
            <h2>Backend Configuration Needed</h2>
            <p>
              The form is valid enough to submit, but the server cannot write to Supabase yet.
              Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`, then restart FastAPI.
            </p>
          </div>
        ) : null}

        {pendingModalTabs.length > 0 ? (
          <div className="intake-modal-backdrop" role="dialog" aria-modal="false" aria-labelledby="pending-tabs-title">
            <div className="intake-modal">
              <h2 id="pending-tabs-title">Complete Pending Tabs</h2>
              <p>Finish these sections before submitting the athlete intake form:</p>
              <ul className="intake-modal-list">
                {pendingModalTabs.map((tab) => (
                  <li key={tab}>{tab}</li>
                ))}
              </ul>
              <button type="button" className="intake-submit" onClick={() => setPendingModalTabs([])}>
                Review Form
              </button>
            </div>
          </div>
        ) : null}

        <div className="intake-tabs" role="tablist" aria-label="Athlete intake sections">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`intake-tab intake-tab-${tabStatusMap[tab.id]} ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="intake-tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {activeTabMissingFields.length > 0 ? (
          <div className="intake-tab-summary">
            <strong>Still needed in this section:</strong> {activeTabMissingFields.slice(0, 4).join(', ')}
            {activeTabMissingFields.length > 4 ? ` +${activeTabMissingFields.length - 4} more` : ''}
          </div>
        ) : (
          <div className="intake-tab-summary intake-tab-summary-complete">
            <strong>This section is complete.</strong>
          </div>
        )}

        <form className="intake-card" onSubmit={handleSubmit}>
          {activeTab === 'athlete' ? (
            <div className="intake-grid">
              <label><span>Name *</span><input className={isInvalidTextField(form.athleteMaster.name, { field: 'athlete.name', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} maxLength={100} value={form.athleteMaster.name} onBlur={() => markTouched('athlete.name')} onChange={(e) => updateSection('athleteMaster', 'name', e.target.value)} disabled required />{(() => { const feedback = getTextFeedback(form.athleteMaster.name, { field: 'athlete.name', required: true, minLength: 2, maxLength: 100, helper: 'Locked to the signed-in athlete account.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Age *</span><input className={isInvalidNumberField(form.athleteMaster.age, { field: 'athlete.age', min: 5, max: 80 }) ? 'intake-input-invalid' : ''} type="number" value={form.athleteMaster.age} onBlur={() => markTouched('athlete.age')} onChange={(e) => updateSection('athleteMaster', 'age', Number(e.target.value))} min={5} max={80} required />{(() => { const feedback = getRangeFeedback(form.athleteMaster.age, { min: 5, max: 80, helper: 'Example: 16' }); return <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> })()}</label>
              <label><span>Gender *</span><select value={form.athleteMaster.gender} onChange={(e) => updateSection('athleteMaster', 'gender', e.target.value)}><option>Male</option><option>Female</option><option>Other</option></select><small className="intake-help info">Choose one of the allowed values.</small></label>
              <label><span>Height (cm) *</span><input type="number" value={form.athleteMaster.heightCm} onChange={(e) => updateSection('athleteMaster', 'heightCm', Number(e.target.value))} min={1} max={260} required /><small className="intake-help info">Example: 170</small></label>
              <label><span>Weight (kg) *</span><input type="number" value={form.athleteMaster.weightKg} onChange={(e) => updateSection('athleteMaster', 'weightKg', Number(e.target.value))} min={1} max={300} required /><small className="intake-help info">Example: 60</small></label>
              <label><span>Academy ID *</span><input className={isInvalidTextField(form.athleteMaster.academyId, { field: 'athlete.academyId', required: true, minLength: 1, maxLength: 50 }) ? 'intake-input-invalid' : ''} maxLength={50} value={form.athleteMaster.academyId} onBlur={() => markTouched('athlete.academyId')} onChange={(e) => updateSection('athleteMaster', 'academyId', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteMaster.academyId, { field: 'athlete.academyId', required: true, minLength: 1, maxLength: 50, caseSensitive: true, helper: 'Example: ACA-001' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Assigned Coach *</span><input className={isInvalidTextField(form.athleteMaster.coachId, { field: 'athlete.coachId', required: true, minLength: 1, maxLength: 80 }) ? 'intake-input-invalid' : ''} maxLength={80} value={form.athleteMaster.coachId} onBlur={() => markTouched('athlete.coachId')} disabled required />{(() => { const feedback = getTextFeedback(form.athleteMaster.coachId, { field: 'athlete.coachId', required: true, minLength: 1, maxLength: 80, helper: 'Locked from your approved coach assignment.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Contact Number *</span><input className={isInvalidTextField(form.athleteMaster.contactNumber, { field: 'athlete.contact', required: true, minLength: 7, maxLength: 20 }) ? 'intake-input-invalid' : ''} minLength={7} maxLength={20} value={form.athleteMaster.contactNumber} onBlur={() => markTouched('athlete.contact')} onChange={(e) => updateSection('athleteMaster', 'contactNumber', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteMaster.contactNumber, { field: 'athlete.contact', required: true, minLength: 7, maxLength: 20, helper: 'Example: +91 9876543210' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Email *</span><input className={touched['athlete.email'] && !/\S+@\S+\.\S+/.test(form.athleteMaster.email) ? 'intake-input-invalid' : ''} type="email" value={form.athleteMaster.email} onBlur={() => markTouched('athlete.email')} onChange={(e) => updateSection('athleteMaster', 'email', e.target.value)} disabled required /><small className="intake-help info">Locked to the signed-in athlete account.</small></label>
            </div>
          ) : null}

          {activeTab === 'family' ? (
            <div className="intake-grid">
              <label><span>Mother Name *</span><input className={isInvalidTextField(form.familyDetails.motherName, { field: 'family.motherName', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.motherName} onBlur={() => markTouched('family.motherName')} onChange={(e) => updateSection('familyDetails', 'motherName', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.motherName, { field: 'family.motherName', required: true, minLength: 2, maxLength: 100, helper: 'Example: Suman Sharma' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Father Name *</span><input className={isInvalidTextField(form.familyDetails.fatherName, { field: 'family.fatherName', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.fatherName} onBlur={() => markTouched('family.fatherName')} onChange={(e) => updateSection('familyDetails', 'fatherName', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.fatherName, { field: 'family.fatherName', required: true, minLength: 2, maxLength: 100, helper: 'Example: Rakesh Sharma' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Mother Occupation *</span><input className={isInvalidTextField(form.familyDetails.motherOccupation, { field: 'family.motherOccupation', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.motherOccupation} onBlur={() => markTouched('family.motherOccupation')} onChange={(e) => updateSection('familyDetails', 'motherOccupation', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.motherOccupation, { field: 'family.motherOccupation', required: true, minLength: 2, maxLength: 100, helper: 'Example: Teacher' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Father Occupation *</span><input className={isInvalidTextField(form.familyDetails.fatherOccupation, { field: 'family.fatherOccupation', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.fatherOccupation} onBlur={() => markTouched('family.fatherOccupation')} onChange={(e) => updateSection('familyDetails', 'fatherOccupation', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.fatherOccupation, { field: 'family.fatherOccupation', required: true, minLength: 2, maxLength: 100, helper: 'Example: Business owner' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Education Level *</span><input className={isInvalidTextField(form.familyDetails.educationLevel, { field: 'family.educationLevel', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.educationLevel} onBlur={() => markTouched('family.educationLevel')} onChange={(e) => updateSection('familyDetails', 'educationLevel', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.educationLevel, { field: 'family.educationLevel', required: true, minLength: 2, maxLength: 100, helper: 'Example: Class 10 / Undergraduate / Postgraduate' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Sibling Details *</span><input className={isInvalidTextField(form.familyDetails.siblingDetails, { field: 'family.siblingDetails', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={250} value={form.familyDetails.siblingDetails} onBlur={() => markTouched('family.siblingDetails')} onChange={(e) => updateSection('familyDetails', 'siblingDetails', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.siblingDetails, { field: 'family.siblingDetails', required: true, minLength: 2, maxLength: 250, helper: 'Example: One elder sister studying in college' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Family Conservative *</span><select value={form.familyDetails.familyConservative} onChange={(e) => updateSection('familyDetails', 'familyConservative', e.target.value)}><option>Yes</option><option>No</option></select><small className="intake-help info">Choose the closest family environment.</small></label>
              <label><span>Discipline Level *</span><input className={isInvalidTextField(form.familyDetails.disciplineLevel, { field: 'family.disciplineLevel', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={100} value={form.familyDetails.disciplineLevel} onBlur={() => markTouched('family.disciplineLevel')} onChange={(e) => updateSection('familyDetails', 'disciplineLevel', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.disciplineLevel, { field: 'family.disciplineLevel', required: true, minLength: 2, maxLength: 100, helper: 'Example: Structured daily routine with clear home rules' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Health Conditions *</span><input className={isInvalidTextField(form.familyDetails.healthConditions, { field: 'family.healthConditions', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={250} value={form.familyDetails.healthConditions} onBlur={() => markTouched('family.healthConditions')} onChange={(e) => updateSection('familyDetails', 'healthConditions', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.healthConditions, { field: 'family.healthConditions', required: true, minLength: 2, maxLength: 250, helper: 'Example: None / Mild asthma / Seasonal allergy' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Father Contact *</span><input className={isInvalidTextField(form.familyDetails.fatherContactNumber, { field: 'family.fatherContact', required: true, minLength: 7, maxLength: 20 }) ? 'intake-input-invalid' : ''} minLength={7} maxLength={20} value={form.familyDetails.fatherContactNumber} onBlur={() => markTouched('family.fatherContact')} onChange={(e) => updateSection('familyDetails', 'fatherContactNumber', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.fatherContactNumber, { field: 'family.fatherContact', required: true, minLength: 7, maxLength: 20, helper: 'Example: +91 9876543210' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Mother Contact *</span><input className={isInvalidTextField(form.familyDetails.motherContactNumber, { field: 'family.motherContact', required: true, minLength: 7, maxLength: 20 }) ? 'intake-input-invalid' : ''} minLength={7} maxLength={20} value={form.familyDetails.motherContactNumber} onBlur={() => markTouched('family.motherContact')} onChange={(e) => updateSection('familyDetails', 'motherContactNumber', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.motherContactNumber, { field: 'family.motherContact', required: true, minLength: 7, maxLength: 20, helper: 'Example: +91 9123456780' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Parent Email *</span><input className={touched['family.parentEmail'] && !/\S+@\S+\.\S+/.test(form.familyDetails.parentEmail) ? 'intake-input-invalid' : ''} type="email" value={form.familyDetails.parentEmail} onBlur={() => markTouched('family.parentEmail')} onChange={(e) => updateSection('familyDetails', 'parentEmail', e.target.value)} required /><small className="intake-help info">Example: parent@example.com</small></label>
              <label className="intake-field-full"><span>Comments *</span><textarea className={isInvalidTextField(form.familyDetails.comments, { field: 'family.comments', required: true, minLength: 2, maxLength: 500 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={500} value={form.familyDetails.comments} onBlur={() => markTouched('family.comments')} onChange={(e) => updateSection('familyDetails', 'comments', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.familyDetails.comments, { field: 'family.comments', required: true, minLength: 2, maxLength: 500, helper: 'Example: Supportive family, no major medical concerns.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
            </div>
          ) : null}

          {activeTab === 'profile' ? (
            <div className="intake-grid">
              <label><span>Class *</span><input className={isInvalidTextField(form.athleteProfile.class, { field: 'profile.class', required: true, minLength: 1, maxLength: 30 }) ? 'intake-input-invalid' : ''} maxLength={30} value={form.athleteProfile.class} onBlur={() => markTouched('profile.class')} onChange={(e) => updateSection('athleteProfile', 'class', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.class, { field: 'profile.class', required: true, minLength: 1, maxLength: 30, helper: 'Example: Class 10' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>School Name *</span><input className={isInvalidTextField(form.athleteProfile.schoolName, { field: 'profile.schoolName', required: true, minLength: 2, maxLength: 150 }) ? 'intake-input-invalid' : ''} maxLength={150} value={form.athleteProfile.schoolName} onBlur={() => markTouched('profile.schoolName')} onChange={(e) => updateSection('athleteProfile', 'schoolName', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.schoolName, { field: 'profile.schoolName', required: true, minLength: 2, maxLength: 150, helper: 'Example: Delhi Public School' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Diet Type</span><select value={form.athleteProfile.dietType} onChange={(e) => updateSection('athleteProfile', 'dietType', e.target.value)}><option>Veg</option><option>Non-Veg</option><option>Mixed</option></select><small className="intake-help info">Choose the athlete's regular diet pattern.</small></label>
              <label><span>Outside Food Frequency</span><select value={form.athleteProfile.outsideFoodFrequency} onChange={(e) => updateSection('athleteProfile', 'outsideFoodFrequency', e.target.value)}><option>Rare</option><option>Weekly</option><option>Frequent</option></select><small className="intake-help info">How often meals come from outside the home.</small></label>
              <label><span>Sleep Time</span><input type="time" value={form.athleteProfile.sleepTime} onChange={(e) => updateSection('athleteProfile', 'sleepTime', e.target.value)} required /><small className="intake-help info">Example: 22:00</small></label>
              <label><span>Wake Time</span><input type="time" value={form.athleteProfile.wakeTime} onChange={(e) => updateSection('athleteProfile', 'wakeTime', e.target.value)} required /><small className="intake-help info">Example: 06:00</small></label>
              <label className="intake-field-full"><span>Friend Circle *</span><textarea className={isInvalidTextField(form.athleteProfile.friendCircle, { field: 'profile.friendCircle', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={250} value={form.athleteProfile.friendCircle} onBlur={() => markTouched('profile.friendCircle')} onChange={(e) => updateSection('athleteProfile', 'friendCircle', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.friendCircle, { field: 'profile.friendCircle', required: true, minLength: 2, maxLength: 250, helper: 'Example: Small close-knit school and academy group.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Anger Pattern *</span><input className={isInvalidTextField(form.athleteProfile.angerPattern, { field: 'profile.angerPattern', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} maxLength={250} value={form.athleteProfile.angerPattern} onBlur={() => markTouched('profile.angerPattern')} onChange={(e) => updateSection('athleteProfile', 'angerPattern', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.angerPattern, { field: 'profile.angerPattern', required: true, minLength: 2, maxLength: 250, helper: 'Example: Gets upset after repeated missed shots.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Sadness Pattern *</span><input className={isInvalidTextField(form.athleteProfile.sadnessPattern, { field: 'profile.sadnessPattern', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} maxLength={250} value={form.athleteProfile.sadnessPattern} onBlur={() => markTouched('profile.sadnessPattern')} onChange={(e) => updateSection('athleteProfile', 'sadnessPattern', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.sadnessPattern, { field: 'profile.sadnessPattern', required: true, minLength: 2, maxLength: 250, helper: 'Example: Withdraws quietly after setbacks.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Academic Performance *</span><input className={isInvalidTextField(form.athleteProfile.academicPerformance, { field: 'profile.academicPerformance', required: true, minLength: 2, maxLength: 100 }) ? 'intake-input-invalid' : ''} maxLength={100} value={form.athleteProfile.academicPerformance} onBlur={() => markTouched('profile.academicPerformance')} onChange={(e) => updateSection('athleteProfile', 'academicPerformance', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.academicPerformance, { field: 'profile.academicPerformance', required: true, minLength: 2, maxLength: 100, helper: 'Example: Strong in academics, steady school record.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Reason for Shooting *</span><input className={isInvalidTextField(form.athleteProfile.reasonForShooting, { field: 'profile.reasonForShooting', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} maxLength={250} value={form.athleteProfile.reasonForShooting} onBlur={() => markTouched('profile.reasonForShooting')} onChange={(e) => updateSection('athleteProfile', 'reasonForShooting', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.reasonForShooting, { field: 'profile.reasonForShooting', required: true, minLength: 2, maxLength: 250, helper: 'Example: Enjoys precision and calm focus in the sport.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label className="intake-field-full"><span>Athlete Goal *</span><textarea className={isInvalidTextField(form.athleteProfile.athleteGoal, { field: 'profile.goal', required: true, minLength: 2, maxLength: 250 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={250} value={form.athleteProfile.athleteGoal} onBlur={() => markTouched('profile.goal')} onChange={(e) => updateSection('athleteProfile', 'athleteGoal', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.athleteProfile.athleteGoal, { field: 'profile.goal', required: true, minLength: 2, maxLength: 250, helper: 'Example: Qualify for state-level shooting trials this year.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
            </div>
          ) : null}

          {activeTab === 'session' ? (
            <div className="intake-grid">
              <label><span>Assigned Coach *</span><input className={isInvalidTextField(form.sessionsLog.coachId, { field: 'session.coachId', required: true, minLength: 1, maxLength: 80 }) ? 'intake-input-invalid' : ''} maxLength={80} value={form.sessionsLog.coachId} onBlur={() => markTouched('session.coachId')} disabled required />{(() => { const feedback = getTextFeedback(form.sessionsLog.coachId, { field: 'session.coachId', required: true, minLength: 1, maxLength: 80, helper: 'Locked from your approved coach assignment.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label><span>Session Date</span><input type="date" value={form.sessionsLog.sessionDate} onChange={(e) => updateSection('sessionsLog', 'sessionDate', e.target.value)} required /><small className="intake-help info">Choose the session day.</small></label>
              <label><span>Start Time</span><input type="time" value={form.sessionsLog.startTime} onChange={(e) => updateSection('sessionsLog', 'startTime', e.target.value)} required /><small className="intake-help info">Session start time.</small></label>
              <label><span>End Time</span><input type="time" value={form.sessionsLog.endTime} onChange={(e) => updateSection('sessionsLog', 'endTime', e.target.value)} required /><small className={`intake-help ${durationPreview > 0 ? 'info' : 'error'}`}>{durationPreview > 0 ? 'Session end time.' : 'End time must be after the start time.'}</small></label>
              <label><span>Training Type</span><select value={form.sessionsLog.trainingType} onChange={(e) => updateSection('sessionsLog', 'trainingType', e.target.value)}><option>Shooting</option><option>Fitness</option><option>Mental</option><option>Recovery</option></select><small className="intake-help info">Select the primary session focus.</small></label>
              <label><span>Location *</span><input className={isInvalidTextField(form.sessionsLog.location, { field: 'session.location', required: true, minLength: 2, maxLength: 120 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={120} value={form.sessionsLog.location} onBlur={() => markTouched('session.location')} onChange={(e) => updateSection('sessionsLog', 'location', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.sessionsLog.location, { field: 'session.location', required: true, minLength: 2, maxLength: 120, helper: 'Example: Main indoor range - Court 2' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <label className="intake-field-full"><span>Notes *</span><textarea className={isInvalidTextField(form.sessionsLog.notes, { field: 'session.notes', required: true, minLength: 2, maxLength: 500 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={500} value={form.sessionsLog.notes} onBlur={() => markTouched('session.notes')} onChange={(e) => updateSection('sessionsLog', 'notes', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.sessionsLog.notes, { field: 'session.notes', required: true, minLength: 2, maxLength: 500, helper: 'Example: Focused on breathing, grip stability, and recovery drills.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
              <div className={`intake-stat ${durationPreview === 0 ? 'intake-stat-invalid' : ''}`}><span>Duration Preview</span><strong>{durationPreview} minutes</strong></div>
            </div>
          ) : null}

          {activeTab === 'physiology' ? (
            <div className="intake-grid">
              <label><span>Recorded Date</span><input type="date" value={form.physiologyData.recordedDate} onChange={(e) => updateSection('physiologyData', 'recordedDate', e.target.value)} required /><small className="intake-help info">Date of this reading.</small></label>
              <label><span>Resting Heart Rate *</span><input className={isInvalidNumberField(form.physiologyData.restingHeartRate, { field: 'physiology.restingHeartRate', min: 40, max: 200 }) ? 'intake-input-invalid' : ''} type="number" min={40} max={200} value={form.physiologyData.restingHeartRate} onBlur={() => markTouched('physiology.restingHeartRate')} onChange={(e) => updateSection('physiologyData', 'restingHeartRate', Number(e.target.value))} required />{(() => { const feedback = getRangeFeedback(form.physiologyData.restingHeartRate, { min: 40, max: 200, helper: 'Example: 60' }); return <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> })()}</label>
              <label><span>Average Heart Rate *</span><input className={isInvalidNumberField(form.physiologyData.avgHeartRate, { field: 'physiology.avgHeartRate', min: 40, max: 200 }) ? 'intake-input-invalid' : ''} type="number" min={40} max={200} value={form.physiologyData.avgHeartRate} onBlur={() => markTouched('physiology.avgHeartRate')} onChange={(e) => updateSection('physiologyData', 'avgHeartRate', Number(e.target.value))} required />{(() => { const feedback = getRangeFeedback(form.physiologyData.avgHeartRate, { min: 40, max: 200, helper: 'Example: 110' }); return <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> })()}</label>
              <label><span>SpO2 *</span><input className={isInvalidNumberField(form.physiologyData.spo2, { field: 'physiology.spo2', min: 80, max: 100 }) ? 'intake-input-invalid' : ''} type="number" min={80} max={100} value={form.physiologyData.spo2} onBlur={() => markTouched('physiology.spo2')} onChange={(e) => updateSection('physiologyData', 'spo2', Number(e.target.value))} required />{(() => { const feedback = getRangeFeedback(form.physiologyData.spo2, { min: 80, max: 100, helper: 'Example: 98' }); return <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> })()}</label>
              <label><span>Breathing Rate</span><input type="number" value={form.physiologyData.breathingRate} onChange={(e) => updateSection('physiologyData', 'breathingRate', Number(e.target.value))} required /><small className="intake-help info">Example: 16 breaths/minute</small></label>
              <label><span>Sleep Hours *</span><input className={isInvalidNumberField(form.physiologyData.sleepHours, { field: 'physiology.sleepHours', min: 0, max: 12 }) ? 'intake-input-invalid' : ''} type="number" step="0.5" min={0} max={12} value={form.physiologyData.sleepHours} onBlur={() => markTouched('physiology.sleepHours')} onChange={(e) => updateSection('physiologyData', 'sleepHours', Number(e.target.value))} required />{(() => { const feedback = getRangeFeedback(form.physiologyData.sleepHours, { min: 0, max: 12, helper: 'Example: 8' }); return <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> })()}</label>
              <label><span>Recovery Score</span><input type="number" min={0} max={100} value={form.physiologyData.recoveryScore} onChange={(e) => updateSection('physiologyData', 'recoveryScore', Number(e.target.value))} required /><small className="intake-help info">Example: 72</small></label>
              <label><span>Stress Score</span><input type="number" min={0} max={100} value={form.physiologyData.stressScore} onChange={(e) => updateSection('physiologyData', 'stressScore', Number(e.target.value))} required /><small className="intake-help info">Example: 32</small></label>
              <label><span>Fatigue Level</span><input type="number" min={0} max={10} value={form.physiologyData.fatigueLevel} onChange={(e) => updateSection('physiologyData', 'fatigueLevel', Number(e.target.value))} required /><small className="intake-help info">Example: 4</small></label>
              <label className="intake-field-full"><span>Remarks *</span><textarea className={isInvalidTextField(form.physiologyData.remarks, { field: 'physiology.remarks', required: true, minLength: 2, maxLength: 500 }) ? 'intake-input-invalid' : ''} minLength={2} maxLength={500} value={form.physiologyData.remarks} onBlur={() => markTouched('physiology.remarks')} onChange={(e) => updateSection('physiologyData', 'remarks', e.target.value)} required />{(() => { const feedback = getTextFeedback(form.physiologyData.remarks, { field: 'physiology.remarks', required: true, minLength: 2, maxLength: 500, helper: 'Example: Recovery looks stable, mild fatigue after fitness block.' }); return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null })()}</label>
            </div>
          ) : null}

          {activeTab === 'psychology' ? (
            <div className="intake-questions">
              {isLoadingQuestions ? <p>Loading psychology questions...</p> : null}
              {questionError ? <p className="intake-error">{questionError}</p> : null}
              {!isLoadingQuestions && questions.length === 0 ? (
                <p className="intake-error">
                  Psychology questions are still loading. Refresh once, and if this stays empty I will tighten that flow next.
                </p>
              ) : null}
              {questions.map((question) => {
                const answer = form.psychologyResponses.find((item) => item.questionId === question.questionId)
                return (
                  <article key={question.questionId} className="question-card">
                    <div className="question-card-header">
                      <div>
                        <p>{question.category}</p>
                        <h3>{question.questionText}</h3>
                      </div>
                      <span>{question.questionType}</span>
                    </div>
                    {question.questionType === 'Scale' ? (
                      <label>
                        <span>Answer Score</span>
                        <input type="range" min={1} max={10} value={answer?.answerScore ?? 5} onChange={(e) => updatePsychologyAnswer(question.questionId, 'answerScore', Number(e.target.value))} />
                        <strong>{answer?.answerScore ?? 5}/10</strong>
                      </label>
                    ) : null}
                    <label>
                      <span>Answer *</span>
                      <textarea className={isInvalidTextField(answer?.answerText ?? '', { field: `psychology.${question.questionId}`, required: true, minLength: 2, maxLength: 500 }) ? 'intake-input-invalid' : ''} maxLength={500} value={answer?.answerText ?? ''} onBlur={() => markTouched(`psychology.${question.questionId}`)} onChange={(e) => updatePsychologyAnswer(question.questionId, 'answerText', e.target.value)} required />
                      {(() => {
                        const feedback = getTextFeedback(answer?.answerText ?? '', {
                          field: `psychology.${question.questionId}`,
                          required: true,
                          minLength: 2,
                          maxLength: 500,
                          helper: question.questionType === 'Text' ? 'Example: Phone notifications and school pressure affected focus.' : 'Example: Felt calm after breathing drills.',
                        })
                        return feedback ? <small className={`intake-help ${feedback.tone}`}>{feedback.text}</small> : null
                      })()}
                    </label>
                  </article>
                )
              })}
            </div>
          ) : null}

          <div className="intake-actions">
            <div>
              {submitState.error ? <p className="intake-error">{submitState.error}</p> : null}
              {submitState.success ? <p className="intake-success">{submitState.success}</p> : null}
            </div>
            <div className="intake-actions-right">
              <Link to="/dashboard" className="intake-secondary">Back to Dashboard</Link>
              <button type="submit" className="intake-submit" disabled={submitState.loading}>
                {submitState.loading ? 'Saving to Supabase...' : 'Submit My Intake'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </section>
  )
}

export default AthleteIntakePage
