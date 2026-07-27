from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.models.interview import *
from app.models.report import InterviewReport
from app.ai.interview.text_evaluator import evaluate
from app.core.exceptions import AppError
from app.utils.enums import InterviewStatus,InterviewType
class InterviewService:
 @staticmethod
 def create(db,user_id,p):
  if p.resume_id:
   from app.models.resume import Resume
   r=db.get(Resume,p.resume_id)
   if not r or r.user_id!=user_id: raise AppError('Resume not found',404,'NOT_FOUND')
  s=InterviewSession(user_id=user_id,role_id=p.target_role_id,resume_id=p.resume_id,interview_type=p.interview_type,mode=p.interview_mode,experience_level=p.experience_level,difficulty=p.difficulty,duration_minutes=p.duration,requested_questions=p.number_of_questions,preferred_language=p.preferred_language,job_description=p.job_description)
  db.add(s); db.flush(); qs=db.scalars(select(InterviewQuestion).where(InterviewQuestion.is_active==True).order_by(func.rand()).limit(p.number_of_questions)).all()
  if not qs: raise AppError('Question bank is empty. Run seed data first',400,'QUESTION_BANK_EMPTY')
  for i,q in enumerate(qs,1): db.add(SessionQuestion(session_id=s.id,question_id=q.id,order_no=i))
  s.status=InterviewStatus.READY; db.commit(); return s
 @staticmethod
 def submit_text(db,user_id,session_id,p):
  s=db.get(InterviewSession,session_id)
  if not s or s.user_id!=user_id: raise AppError('Interview session not found',404,'NOT_FOUND')
  if s.status not in [InterviewStatus.IN_PROGRESS,InterviewStatus.READY]: raise AppError('Interview is not accepting answers',409,'INVALID_STATE')
  sq=db.scalar(select(SessionQuestion).where(SessionQuestion.session_id==s.id,SessionQuestion.question_id==p.question_id))
  if not sq: raise AppError('Question is not part of this session',404,'NOT_FOUND')
  if db.scalar(select(InterviewAnswer).where(InterviewAnswer.session_question_id==sq.id)): raise AppError('Question already answered',409,'DUPLICATE_ANSWER')
  q=db.get(InterviewQuestion,p.question_id); a=InterviewAnswer(session_question_id=sq.id,answer_text=p.answer_text,transcript=p.answer_text); db.add(a); db.flush(); final,cats,signals,strengths,weaknesses=evaluate(p.answer_text,q.expected_keywords,s.interview_type in [InterviewType.BEHAVIORAL,InterviewType.HR]); db.add(AnswerEvaluation(answer_id=a.id,final_score=final,category_scores=cats,raw_signals=signals,strengths=strengths,weaknesses=weaknesses,feedback='AI feedback is advisory and should be reviewed by the user.',improved_answer=None)); s.status=InterviewStatus.IN_PROGRESS; s.current_order=max(s.current_order,sq.order_no); db.commit(); return {'score':final,'category_scores':cats,'strengths':strengths,'weaknesses':weaknesses}
 @staticmethod
 def complete(db,user_id,session_id):
  s=db.get(InterviewSession,session_id)
  if not s or s.user_id!=user_id: raise AppError('Interview session not found',404,'NOT_FOUND')
  scores=db.scalars(select(AnswerEvaluation.final_score).join(InterviewAnswer,InterviewAnswer.id==AnswerEvaluation.answer_id).join(SessionQuestion,SessionQuestion.id==InterviewAnswer.session_question_id).where(SessionQuestion.session_id==s.id)).all()
  if not scores: raise AppError('Submit at least one answer before completion',400,'NO_ANSWERS')
  avg=round(sum(scores)/len(scores),2); label='Excellent' if avg>=80 else 'Good' if avg>=65 else 'Developing' if avg>=45 else 'Needs Practice'; report=db.scalar(select(InterviewReport).where(InterviewReport.session_id==s.id))
  data=dict(user_id=user_id,session_id=s.id,overall_score=avg,performance_label=label,category_scores={'overall':avg},executive_summary='AI-assisted advisory report based mainly on answer content.',strengths=['Completed interview practice'],growth_areas=['Review question-level feedback'],question_feedback=[],recommendations=['Practice another interview after reviewing feedback'])
  if report:
   for k,v in data.items(): setattr(report,k,v)
  else: report=InterviewReport(**data); db.add(report)
  s.status=InterviewStatus.COMPLETED; db.commit(); return report
