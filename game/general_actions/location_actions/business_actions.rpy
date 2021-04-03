init 0 python:
    def sleep_action_requirement():
        if time_of_day != 4:
            return "Too early to sleep"
        else:
            return True

    def faq_action_requirement():
        return True

    def hr_work_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        else:
            return True

    def research_work_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        elif mc.business.active_research_design is None:
            return "No research project set"
        else:
            return True

    def supplies_work_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        else:
            return True

    def market_work_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        elif mc.business.sale_inventory.get_any_serum_count() == 0:
            return "Nothing to sell"
        return True

    def production_work_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        elif len(mc.business.serum_production_array) == 0:
            return "No serum design set"
        else:
            return True

    def interview_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        elif mc.business.get_employee_count() >= mc.business.max_employee_count:
            return "At employee limit"
        else:
            return True

    def serum_design_action_requirement():
        if time_of_day >= 4:
            return "Too late to work"
        else:
            return True

    def research_select_action_requirement():
        return True

    def production_select_action_requirement():
        return True

    def trade_serum_action_requirement():
        return True

    def sell_serum_action_requirement():
        return True

    def pick_supply_goal_action_requirement():
        return True

    def policy_purchase_requirement():
        return True

    def head_researcher_select_requirement():
        if mc.business.head_researcher is not None:
            return False
        elif __builtin__.len(mc.business.research_team) == 0:
            return "Nobody to pick"
        else:
            return True

    def pick_company_model_requirement():
        if mc.business.company_model is not None:
            return False
        elif not public_advertising_license_policy.is_active():
            return False
        elif mc.business.get_employee_count() == 0:
            return "Nobody to pick"
        else:
            return True

    def set_uniform_requirement():
        return strict_uniform_policy.is_active()

    def set_serum_requirement():
        if daily_serum_dosage_policy.is_owned() and not daily_serum_dosage_policy.is_active():
            return "Policy not active"
        else:
            return daily_serum_dosage_policy.is_active()

    def review_designs_action_requirement():
        return True

label give_serum(the_person):
    call screen serum_inventory_select_ui(mc.inventory, the_person)
    if not _return == "None":
        $ the_serum = _return
        "You decide to give [the_person.title] a dose of [the_serum.name]."
        $ mc.inventory.change_serum(the_serum,-1)
        $ the_person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
        return the_serum
    else:
        "You decide not to give [the_person.title] anything."
        return False

label sleep_action_description:
    "You go to bed after a hard days work."
    call advance_time from _call_advance_time
    return

label faq_action_description:
    call faq_loop
    return

label hr_work_action_description:
    $ mc.business.player_hr()
    call advance_time from _call_advance_time_1
    return

label research_work_action_description:
    $ mc.business.player_research()
    call advance_time from _call_advance_time_2
    return

label supplies_work_action_description:
    $ mc.business.player_buy_supplies()
    call advance_time from _call_advance_time_3
    return

label market_work_action_description:
    $ mc.business.player_market()
    call advance_time from _call_advance_time_4

    return

label production_work_action_description:
    $ mc.business.player_production()
    call advance_time from _call_advance_time_5
    return

label interview_action_description:
    $ count = 3 #Num of people to generate, by default is 3. Changed with some policies
    if recruitment_batch_three_policy.is_active():
        $ count = 10
    elif recruitment_batch_two_policy.is_active():
        $ count = 6
    elif recruitment_batch_one_policy.is_active():
        $ count = 4

    $ interview_cost = 50
    "Bringing in [count] people for an interview will cost $[interview_cost]. Do you want to spend time interviewing potential employees?"
    menu:
        "Yes, I'll pay the cost. -$[interview_cost]":
            $ mc.business.funds += -interview_cost
            $ clear_scene()
            $ renpy.free_memory() #Try and free available memory
            python: #Build our list of candidates with our proper recruitment requirements
                candidates = []

                for x in range(0,count+1): #NOTE: count is given +1 because the screen tries to pre-calculate the result of button presses. This leads to index out-of-bounds, unless we pad it with an extra character (who will not be reached).
                    candidates.append(make_person())

                reveal_count = 0
                reveal_sex = False
                if recruitment_knowledge_one_policy.is_active():
                    reveal_count += 2
                if recruitment_knowledge_two_policy.is_active():
                    reveal_count += 2
                if recruitment_knowledge_three_policy.is_active():
                    reveal_count += 1
                    reveal_sex = True
                if recruitment_knowledge_four_policy.is_active():
                    reveal_count += 1
                for a_candidate in candidates:
                    for x in __builtin__.range(0,reveal_count): #Reveal all of their opinions based on our policies.
                        a_candidate.discover_opinion(a_candidate.get_random_opinion(include_known = False, include_sexy = reveal_sex),add_to_log = False) #Get a random opinion and reveal it.
            call hire_select_process(candidates) from _call_hire_select_process
            $ candidates = [] #Prevent it from using up extra memory
            $ renpy.free_memory() #Try and force a clean up of unused memory.

            if not _return == "None":
                $ new_person = _return
                $ new_person.generate_home() #Generate them a home location so they have somewhere to go at night.
                call hire_someone(new_person, add_to_location = True) from _call_hire_someone #
                $ new_person.set_title(get_random_title(new_person))
                $ new_person.set_possessive_title(get_random_possessive_title(new_person))
                $ new_person.set_mc_title(get_random_player_title(new_person))
            else:
                "You decide against hiring anyone new for now."
            call advance_time from _call_advance_time_6
        "Nevermind.":
            pass
    return

label hire_select_process(candidates):
    hide screen main_ui #NOTE: We have to hide all of these screens because we are using a fake (aka. non-screen) background for this. We're doing that so we can use the normal draw_person call for them.
    hide screen phone_hud_ui
    hide screen business_ui
    hide screen goal_hud_ui
    $ show_candidate(candidates[0]) #Show the first candidate, updates are taken care of by actions within the screen.
    show bg paper_menu_background #Show a paper background for this scene.
    $ count = __builtin__.len(candidates)-1
    call screen interview_ui(candidates,count)
    $ renpy.scene()
    show screen phone_hud_ui
    show screen business_ui
    show screen goal_hud_ui
    show screen main_ui
    $ clear_scene()
    $ mc.location.show_background()

    return _return


label hire_someone(new_person, add_to_location = False): # Breaks out some of the functionality of hiring someone into an independent lable.
    "You complete the necessary paperwork and hire [new_person.name]. What division do you assign them to?"
    menu:
        "Research and Development":
            $ mc.business.add_employee_research(new_person, add_to_location)

        "Production":
            $ mc.business.add_employee_production(new_person, add_to_location)

        "Supply Procurement":
            $ mc.business.add_employee_supply(new_person, add_to_location)

        "Marketing":
            $ mc.business.add_employee_marketing(new_person, add_to_location)

        "Human Resources":
            $ mc.business.add_employee_hr(new_person, add_to_location)

    return

label serum_design_action_description:
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    call screen serum_design_ui(SerumDesign(),[]) #This will return the final serum design, or None if the player backs out.
    $ the_serum = _return

    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    if not the_serum == "None":
        $ name = renpy.input("Please give this serum design a name.")
        $ the_serum.name = name
        $ mc.business.add_serum_design(the_serum)
        $ mc.business.listener_system.fire_event("new_serum", the_serum = the_serum)
        $ the_serum = None
        call advance_time from _call_advance_time_7
    else:
        "You decide not to spend any time designing a new serum type."
    return

label research_select_action_description:
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    call screen serum_select_ui
    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    if not _return == "None":
        $mc.business.set_serum_research(_return)
        "You change your research to [_return.name]."
    else:
        "You decide to leave your lab's current research topic as it is."
    return

label production_select_action_description: #TODO: Change this to allow you to select which line of serum you are changing!
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    call screen serum_production_select_ui
    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    return

label trade_serum_action_description:
    "You step into the stock room to check what you currently have produced."
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.inventory,mc.business.inventory)
    $ renpy.block_rollback()
    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    return

label sell_serum_action_description:
    "You look through your stock of serum, marking some to be sold by your marketing team."
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.business.inventory,mc.business.sale_inventory,"Production Stockpile","Sales Stockpile")
    $ renpy.block_rollback()

    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    return

label review_designs_action_description:
    hide screen main_ui
    hide screen phone_hud_ui
    hide screen business_ui
    $ renpy.block_rollback() #Block rollback to prevent any strange issues with references being lost.
    call screen review_designs_screen()
    $ renpy.block_rollback()

    show screen phone_hud_ui
    show screen business_ui
    show screen main_ui
    return


label pick_supply_goal_action_description:
    $ amount = renpy.input("How many units of serum supply would you like your supply procurement team to keep stocked?")
    $ amount = amount.strip()

    while not amount.isdigit():
        $ amount = renpy.input("Please put in an integer value.")

    $ amount = int(amount)
    $ mc.business.supply_goal = amount
    if amount <= 0:
        "You tell your team to keep [amount] units of serum supply stocked. They question your sanity, but otherwise continue with their work. Perhaps you should use a positive number."
    else:
        "You tell your team to keep [amount] units of serum supply stocked."

    return

label policy_purchase_description:
    call screen policy_selection_screen_v2() #policy_selection_screen
    return

label head_researcher_select_description:
    call screen employee_overview(white_list = mc.business.research_team, person_select = True)
    $ new_head = _return
    $ mc.business.head_researcher = new_head
    $ new_head.add_role(head_researcher)
    $ del new_head
    return

label pick_company_model_description:
    call screen employee_overview(person_select = True)
    if not _return is None:
        $ mc.business.hire_company_model(_return)
    return

label set_uniform_description:
    #First, establish the maximums the uniform can reach.
    $ slut_limit, underwear_limit, limited_to_top = mc.business.get_uniform_limits() #Function generates all uniform related limits to keep them consistent between events and active/deavtive policies.


    #Some quick holding variables to store the options picked.
    $ selected_div = None
    $ uniform_mode = None
    $ uniform_type = None
    menu:
        "Add a complete outfit" if not limited_to_top:
            $ uniform_mode = "full"

        "Add a complete outfit\n{color=#ff0000}{size=18}Requires: Reduced Coverage Corporate Uniforms{/size}{/color} (disabled)" if limited_to_top:
            pass

        "Add an overwear set":
            $ uniform_mode = "over"

        "Add an underwear set" if not limited_to_top:
            $ uniform_mode = "under"

        "Add an underwear set\n{color=#ff0000}{size=18}Requires: Reduced Coverage Corporate Uniforms{/size}{/color} (disabled)" if limited_to_top:
            pass

        "Remove a uniform or set":
            $ uniform_mode = "delete"


    menu:
        "Company Wide Uniforms\n{color=#ff0000}{size=18}Can be worn by everyone{/size}{/color}": #Get the wardrobe we are going to be modifying.
            $ selected_div = mc.business.all_uniform

        "R&D Uniforms":
            $ selected_div = mc.business.r_uniform

        "Production Uniforms":
            $ selected_div = mc.business.p_uniform

        "Supply Procurement Uniforms":
            $ selected_div = mc.business.s_uniform

        "Marketing Uniforms":
            $ selected_div = mc.business.m_uniform

        "Human Resources Uniforms":
            $ selected_div = mc.business.h_uniform

    if uniform_mode == "delete":
        call screen outfit_delete_manager(selected_div) #Calls the wardrobe screen and lets teh player delete whatever they want.

    else:
        if uniform_mode == "full":
            call outfit_master_manager(slut_limit = slut_limit) from _call_outfit_master_manager_3
            $ new_outfit = _return
            if new_outfit is None:
                return


            $ mc.business.listener_system.fire_event("add_uniform", the_outfit = new_outfit, the_type = "full")
            $ selected_div.add_outfit(new_outfit.get_copy())

        elif uniform_mode == "under":
            call outfit_master_manager(slut_limit = underwear_limit, show_outfits = False, show_underwear = True, show_overwear = False) from _call_outfit_master_manager_4
            $ new_outfit = _return
            if new_outfit is None:
                return

            $ mc.business.listener_system.fire_event("add_uniform", the_outfit = new_outfit, the_type = "under")
            $ selected_div.add_underwear_set(new_outfit.get_copy())

        else: #uniform_mode == "over":
            call outfit_master_manager(slut_limit = slut_limit, show_outfits = False, show_underwear = False, show_overwear = True) from _call_outfit_master_manager_5
            $ new_outfit = _return
            if new_outfit is None:
                return

            $ mc.business.listener_system.fire_event("add_uniform", the_outfit = new_outfit, the_type = "over")
            $ selected_div.add_overwear_set(new_outfit.get_copy())


    return

label set_serum_description: #TODO: Add a special screen for all of this instead of doing it through menus
    "Which divisions would you like to set a daily serum for?"
    $ selected_div = None
    $ selected_serum = None

    menu:
        "All":
            $ selected_div = "All"

        "Research and Development":
            $ selected_div = "R"

        "Production":
            $ selected_div = "P"

        "Supply Procurement":
            $ selected_div = "S"

        "Marketing":
            $ selected_div = "M"

        "Human Resources":
            $ selected_div = "H"

    menu:
        "Pick a new serum":
            call screen serum_inventory_select_ui(mc.business.inventory)
            $ selected_serum = _return

        "Clear existing serum":
            $ selected_serum = None

    if selected_serum == "None": #IF we didn't select an actual serum, just return and don't chagne anything.
        return

    if selected_div == "All":
        $ mc.business.m_serum = selected_serum
        $ mc.business.p_serum = selected_serum
        $ mc.business.r_serum = selected_serum
        $ mc.business.s_serum = selected_serum
        $ mc.business.h_serum = selected_serum

    elif selected_div == "R":
        $ mc.business.r_serum = selected_serum

    elif selected_div == "P":
        $ mc.business.p_serum = selected_serum

    elif selected_div == "S":
        $ mc.business.s_serum = selected_serum

    elif selected_div == "M":
        $ mc.business.m_serum = selected_serum

    elif selected_div == "H":
        $ mc.business.h_serum = selected_serum

    return
