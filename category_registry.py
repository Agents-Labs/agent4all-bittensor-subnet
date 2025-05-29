categories = {
    "data-analyst": {"description": "Data Analyst Agent", "status": "approved"},
    "finance": {"description": "Finance Agent", "status": "approved"},
    "image": {"description": "Image Agent", "status": "approved"},
    "image-to-text": {"description": "Image-to-Text Agent", "status": "approved"},
    "markdown": {"description": "Markdown Agent", "status": "approved"},
    "planning": {"description": "Planning Agent", "status": "approved"},
    "programming": {"description": "Programming Agent", "status": "approved"},
    "recommendation": {"description": "Recommendation Agent", "status": "approved"},
    "research": {"description": "Research Agent", "status": "approved"},
    "shopping": {"description": "Shopping Agent", "status": "approved"},
    "single": {"description": "Single Agent", "status": "approved"},
    "video": {"description": "Video Agent", "status": "approved"},
    "websearch": {"description": "Websearch Agent", "status": "approved"},
    "wikipedia": {"description": "Wikipedia Agent", "status": "approved"}
}

def get_categories(status="approved"):
    return [k for k, v in categories.items() if v["status"] == status]

def get_category_info(category):
    return categories.get(category)

def propose_category(category, description, benchmark, io_format, validation_strategy):
    categories[category] = {
        "description": description,
        "benchmark": benchmark,
        "io_format": io_format,
        "validation_strategy": validation_strategy,
        "status": "pending"
    }
    return True

def approve_category(category):
    if category in categories:
        categories[category]["status"] = "approved"
        return True
    return False 