from fastapi import FastAPI, HTTPException
from app.schemas import AIRequest, AIResponse
from app.orchestrator import Orchestrator
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.state_machine.states import ConversationState

app = FastAPI(
    title="Jamie AI Setter",
    description="State-driven AI Setter chatbot service",
    version="1.0.0",
)

# Initialize orchestrator once
orchestrator = Orchestrator()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")


@app.post("/process-message", response_model=AIResponse)
def process_message(request: AIRequest):
    # ... (Keep your existing logic exactly the same) ...
    try:
        # Convert state string to enum
        if request.current_state not in ConversationState.__members__:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid conversation state: {request.current_state}",
            )

        current_state = ConversationState[request.current_state]

        result = orchestrator.process_message(
            user_message=request.message,
            current_state=current_state,
            extracted_attributes=request.user_attributes,
        )

        return AIResponse(
            reply=result["reply"],
            next_state=result["next_state"],
            extracted_attributes=result.get("extracted_attributes"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
# def process_message(request: AIRequest):
#     """
#     Main endpoint for processing a single user message.
#     """

#     try:
#         # Convert state string to enum
#         #current_state = ConversationState(request.current_state)
        
#         if request.current_state not in ConversationState.__members__:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid conversation state: {request.current_state}",
#             )

#         current_state = ConversationState[request.current_state]

#         result = orchestrator.process_message(
#             user_message=request.message,
#             current_state=current_state,
#             extracted_attributes=request.user_attributes,
#         )

#         return AIResponse(
#             reply=result["reply"],
#             next_state=result["next_state"],
#             extracted_attributes=result.get("extracted_attributes"),
#             #extracted_attributes=None,  # Phase 2: attribute extraction
#         )

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     # except Exception as e:
#     #     raise HTTPException(
#     #         status_code=500,
#     #         detail="Internal server error while processing AI message",
#     #     )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )
# def process_message(request: AIRequest):
#     # ... (Keep your existing logic exactly the same) ...
#     try:
#         # Convert state string to enum
#         if request.current_state not in ConversationState.__members__:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid conversation state: {request.current_state}",
#             )

#         current_state = ConversationState[request.current_state]

#         result = orchestrator.process_message(
#             user_message=request.message,
#             current_state=current_state,
#             extracted_attributes=request.user_attributes,
#         )

#         return AIResponse(
#             reply=result["reply"],
#             next_state=result["next_state"],
#             extracted_attributes=result.get("extracted_attributes"),
#         )

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )