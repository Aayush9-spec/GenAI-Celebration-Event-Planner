from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class BudgetItem(BaseModel):
    category: str
    amount: float
    percentage: float
    notes: Optional[str] = None


class BudgetBreakdown(BaseModel):
    total: float
    currency: str = "INR"
    items: List[BudgetItem] = []


class TimelineMilestone(BaseModel):
    offset: int
    unit: str = "week"
    task: str
    category: Optional[str] = None
    priority: Optional[str] = "medium"


class Timeline(BaseModel):
    total_weeks: Optional[int] = None
    milestones: List[TimelineMilestone] = []


class VendorItem(BaseModel):
    task: str
    done: bool = False
    deadline_weeks_before: Optional[int] = None
    tips: Optional[str] = None


class VendorCategory(BaseModel):
    name: str
    items: List[VendorItem] = []


class VendorChecklist(BaseModel):
    categories: List[VendorCategory] = []


class ThemeIdea(BaseModel):
    title: str
    description: str
    estimated_cost_impact: Optional[str] = "medium"


class ThemeIdeas(BaseModel):
    recommended_theme: Optional[str] = None
    color_palette: List[str] = []
    ideas: List[ThemeIdea] = []
    personalization_tips: List[str] = []


class PlanOut(BaseModel):
    id: int
    event_id: int
    budget_breakdown: Optional[Dict[str, Any]] = None
    timeline: Optional[Dict[str, Any]] = None
    vendor_checklist: Optional[Dict[str, Any]] = None
    theme_ideas: Optional[Dict[str, Any]] = None
    created_at: str

    model_config = {"from_attributes": True}

    def model_post_init(self, __context):
        # Serialise datetime to string
        if hasattr(self, "created_at") and not isinstance(self.created_at, str):
            object.__setattr__(self, "created_at", str(self.created_at))
