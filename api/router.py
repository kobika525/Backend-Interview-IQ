from fastapi import APIRouter
from app.api.routes import auth,users,resumes,careers,interviews,reports,progress,subscriptions,roadmaps,resources,skills,achievements,notifications,billing,support,jobs,admin
api_router=APIRouter()
for r in [auth.router,users.router,resumes.router,careers.router,interviews.router,reports.router,progress.router,subscriptions.router,roadmaps.router,resources.router,skills.router,achievements.router,notifications.router,billing.router,support.router,jobs.router,admin.router]: api_router.include_router(r)
