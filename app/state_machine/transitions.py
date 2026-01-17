from typing import Dict, Optional
from app.state_machine.states import ConversationState
#from app.state_machine.exit_rules import should_exit_entry 
#from app.state_machine.exit_rules import should_exit_rapport
from app.state_machine.exit_rules import entry_boundary_action
from app.state_machine.exit_rules import (
    has_sufficient_capacity,
    get_financial_bucket,
    classify_relationship_goal,
    normalize_text,
    should_exit_entry,
    should_exit_rapport,
    should_exit_problem_discovery,
    should_exit_coaching_transition,
    entry_boundary_action,
    is_stall_response,
    has_concrete_detail,
    is_problem_signal,
    confirms_pattern,
    seeks_help,
    expresses_exhaustion,
    gives_permission,
    declines_permission,
    is_location_eligible,
    expresses_investment_mindset,
)


# ALLOWED_LOCATIONS = {"US", "USA", "CANADA", "EU", "UK"}


def determine_next_state(
    current_state: ConversationState,
    user_message: str,
    extracted_attributes: Optional[Dict[str, str]] = None,
) -> ConversationState:
    """
    Determines the next conversation state based on
    the current state and extracted user attributes.
    """

    if extracted_attributes is None :
        extracted_attributes = {}
    #extracted_attributes = extracted_attributes or {}

    # -------------------------
    # LINEAR FLOW STATES
    # -------------------------

    # if current_state == ConversationState.ENTRY:
    #     if should_exit_entry(user_message):
    #         return ConversationState.RAPPORT
    #     return ConversationState.ENTRY

################ ENTRY STATE ########################

    if current_state == ConversationState.ENTRY:
        normalized = normalize_text(user_message)

        action = entry_boundary_action(normalized, extracted_attributes)

        if action == "HARD_STOP":
            return ConversationState.END

        if action == "WARN_ABUSE":
            return ConversationState.ENTRY

        if should_exit_entry(normalized):
            return ConversationState.RAPPORT

        return ConversationState.ENTRY


    # if current_state == ConversationState.RAPPORT:
    #     if should_exit_rapport(user_message):
    #         return ConversationState.PROBLEM_DISCOVERY
    #     return ConversationState.RAPPORT

############### RAPPORT STATE ########################

    if current_state == ConversationState.RAPPORT:
        normalized = normalize_text(user_message)

        if seeks_help(normalized):
            return ConversationState.PROBLEM_DISCOVERY
        
        stall_count = extracted_attributes.get("stall_count", 0)

        if is_stall_response(normalized):
            stall_count += 1
            extracted_attributes["stall_count"] = stall_count
        elif has_concrete_detail(normalized):
            # Reset stall counter on specificity
            extracted_attributes["stall_count"] = 0

        # Stay in RAPPORT unless normal exit rules apply
        if should_exit_rapport(normalized):
            return ConversationState.PROBLEM_DISCOVERY

        return ConversationState.RAPPORT

############### PROBLEM DISCOVERY STATE ###################

    # if current_state == ConversationState.PROBLEM_DISCOVERY:
    #     if should_exit_problem_discovery(user_message):
    #         return ConversationState.COACHING_TRANSITION
    #     return ConversationState.PROBLEM_DISCOVERY

    # if current_state == ConversationState.PROBLEM_DISCOVERY:
    #     normalized = normalize_text(user_message)

    #     # Initialize counters
    #     signal_count = extracted_attributes.get("problem_signal_count", 0)
    #     confirmed = extracted_attributes.get("problem_confirmed", False)

    #     # Detect signals
    #     if is_problem_signal(normalized):
    #         signal_count += 1
    #         extracted_attributes["problem_signal_count"] = signal_count

    #     # Confirm pattern
    #     if confirms_pattern(normalized) or signal_count >= 2:
    #         extracted_attributes["problem_confirmed"] = True
    #         confirmed = True

    #     # Exit only on help-seeking or exhaustion
    #     if seeks_help(normalized) or expresses_exhaustion(normalized):
    #         return ConversationState.COACHING_TRANSITION

    #     # Otherwise stay in PROBLEM_DISCOVERY
    #     return ConversationState.PROBLEM_DISCOVERY

    if current_state == ConversationState.PROBLEM_DISCOVERY:
        normalized = normalize_text(user_message)

        # Initialize memory
        signal_count = extracted_attributes.get("problem_signal_count", 0)
        confirmed = extracted_attributes.get("problem_confirmed", False)

        # Signal detection
        if is_problem_signal(normalized):
            signal_count += 1
            extracted_attributes["problem_signal_count"] = signal_count

        # Confirmation
        if confirms_pattern(normalized) or signal_count >= 2:
            extracted_attributes["problem_confirmed"] = True
            confirmed = True

        # Exit conditions
        if seeks_help(normalized) or expresses_exhaustion(normalized):
            return ConversationState.COACHING_TRANSITION

        #  CONVERGENCE ENFORCEMENT (ANCHOR + HOLD)
        if confirmed:
            # Do NOT continue discovery once pattern is clear
            return ConversationState.PROBLEM_DISCOVERY

        return ConversationState.PROBLEM_DISCOVERY


############# COACHING TRANSITION STATE ##################

    # if current_state == ConversationState.COACHING_TRANSITION:
    #     if should_exit_coaching_transition(user_message):
    #         return ConversationState.QUAL_LOCATION
    #     return ConversationState.COACHING_TRANSITION

    if current_state == ConversationState.COACHING_TRANSITION:
        normalized = normalize_text(user_message)

        # User gives permission → begin qualification
        if gives_permission(normalized):
            return ConversationState.QUAL_LOCATION

        # User declines or hesitates → stay here, do not push
        if declines_permission(normalized):
            return ConversationState.COACHING_TRANSITION

        # Default: hold and wait
        return ConversationState.COACHING_TRANSITION


################ QUAL LOCATION STATE ####################

    # if current_state == ConversationState.QUAL_LOCATION:
    #     normalized = normalize_text(user_message)

    #     location = extract_location(normalized)
    #     if location is None:
    #         return ConversationState.QUAL_LOCATION

    #     # Eligible → continue
    #     return ConversationState.QUAL_RELATIONSHIP_GOAL

    if current_state == ConversationState.QUAL_LOCATION:
        normalized = normalize_text(user_message)

        # Eligible country → continue qualification
        if is_location_eligible(normalized):
            return ConversationState.QUAL_RELATIONSHIP_GOAL

        # Ineligible or unclear → route low ticket
        return ConversationState.ROUTE_LOW_TICKET

################ QUAL RELATIONSHIP GOAL #########################

    # if current_state == ConversationState.QUAL_RELATIONSHIP_GOAL:
    #     normalized = normalize_text(user_message)

    #     if not has_relationship_goal(normalized):
    #         return ConversationState.QUAL_RELATIONSHIP_GOAL

    #     return ConversationState.QUAL_FITNESS

    if current_state == ConversationState.QUAL_RELATIONSHIP_GOAL:
        normalized = normalize_text(user_message)

        goal = classify_relationship_goal(normalized)

        # Any recognizable goal → continue qualification
        if goal in {"supported", "unsupported"}:
            return ConversationState.QUAL_FITNESS

        # Unclear → ask again (prompt handles this)
        return ConversationState.QUAL_RELATIONSHIP_GOAL


################## QUAL FITNESS ########################

    # if current_state == ConversationState.QUAL_FITNESS:
    #     normalized = normalize_text(user_message)

    #     if not has_fitness_level(normalized):
    #         return ConversationState.QUAL_FITNESS

    #     return ConversationState.QUAL_FINANCE

    if current_state == ConversationState.QUAL_FITNESS:
        normalized = normalize_text(user_message)

        # Rare low-capacity → free route
        if not has_sufficient_capacity(normalized):
            return ConversationState.ROUTE_LOW_TICKET

        # Default: continue qualification
        return ConversationState.QUAL_FINANCE


    # -------------------------
    # FINANCIAL ROUTING LOGIC
    # -------------------------

    if current_state == ConversationState.QUAL_FINANCE:
        normalized = normalize_text(user_message)

        # bucket = get_financial_bucket(normalized)
        # if bucket is None:
        #     return ConversationState.QUAL_FINANCE
        # If finance already completed, route immediately
        # if extracted_attributes.get("finance_completed"):
        #     bucket = extracted_attributes.get("financial_bucket")

        #     if bucket == "low":
        #         return ConversationState.ROUTE_LOW_TICKET

        #     return ConversationState.ROUTE_HIGH_TICKET

        # # Otherwise, detect finance normally
        # bucket = get_financial_bucket(normalized)
        # if bucket is None:
        #     return ConversationState.QUAL_FINANCE

        # # Mark finance as completed
        # extracted_attributes["finance_completed"] = True
        # extracted_attributes["financial_bucket"] = bucket

        # if bucket == "low":
        #     return ConversationState.ROUTE_LOW_TICKET

        # return ConversationState.ROUTE_HIGH_TICKET

    if current_state == ConversationState.QUAL_FINANCE:
        normalized = normalize_text(user_message)

        # SAFETY: low capacity anywhere → low route
        if not has_sufficient_capacity(normalized):
            return ConversationState.ROUTE_LOW_TICKET

        # Explicit finance language
        bucket = get_financial_bucket(normalized)
        if bucket:
            extracted_attributes["finance_completed"] = True
            extracted_attributes["financial_bucket"] = bucket

            if bucket == "low":
                return ConversationState.ROUTE_LOW_TICKET

            return ConversationState.ROUTE_HIGH_TICKET

        # Indirect investment mindset → HIGH
        if expresses_investment_mindset(normalized):
            extracted_attributes["finance_completed"] = True
            extracted_attributes["financial_bucket"] = "high"
            return ConversationState.ROUTE_HIGH_TICKET

        # Otherwise, stay and ask once more
        return ConversationState.QUAL_FINANCE



        # if bucket == "low":
        #     return ConversationState.ROUTE_LOW_TICKET

        # return ConversationState.ROUTE_HIGH_TICKET


    # -------------------------
    # TERMINAL STATES
    # -------------------------

    if current_state in {
        ConversationState.ROUTE_HIGH_TICKET,
        ConversationState.ROUTE_LOW_TICKET,
    }:
        return ConversationState.END

    return ConversationState.END

