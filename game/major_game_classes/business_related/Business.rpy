init -2 python:
    class Business(renpy.store.object):
        # main jobs to start with:
        # 1) buying raw supplies.
        # 2) researching new serums.
        # 2a) The player (only) designs new serums to be researched.
        # 3) working in the lab to produce serums.
        # 4) Working in marketing. Increases volume you can sell, and max price you can sell for.
        # 5) Packaging and selling serums that have been produced.
        # 6) General secretary work. Starts at none needed, grows as your company does (requires an "HR", eventually). Maybe a general % effectivness rating.
        def __init__(self, name, m_div, p_div, r_div, s_div, h_div):
            self.name = name
            self.funds = 1000 #Your starting wealth.

            self.bankrupt_days = 0 #How many days you've been bankrupt. If it hits the max value you lose.
            self.max_bankrupt_days = 3 #How many days you can be negative without loosing the game. Can be increased through research.

            self.m_div = m_div #The physical locations of all of the teams, so you can move to different offices in the future.
            self.p_div = p_div
            self.r_div = r_div
            self.s_div = s_div
            self.h_div = h_div

            # Uniforms are stored as a wardrobe specific to each department. There is also a company wide wardrobe that can be accessed.
            # self.all_uniform = Wardrobe(self.name + " All Wardrobe")
            self.m_uniform = Wardrobe(self.name + " Marketing Wardrobe")
            self.p_uniform = Wardrobe(self.name + " Production Wardrobe")
            self.r_uniform = Wardrobe(self.name + " Research Wardrobe")
            self.s_uniform = Wardrobe(self.name + " Supply Wardrobe")
            self.h_uniform = Wardrobe(self.name + " HR Wardrobe")
            self.all_uniform = Wardrobe(self.name + " Shared Uniform Wardrobe")

            self.m_serum = None #These are the serums given to the different departments if the daily serum dosage policy is researched.
            self.p_serum = None
            self.r_serum = None
            self.s_serum = None
            self.h_serum = None

            # self.research_team = [] #Researches new serums that the player designs, does theoretical research into future designs, or improves old serums slightly over time
            # self.market_team = [] # Increases company marketability. Raises max price serum can be sold for, and max volume that can be sold.
            # self.supply_team = [] # Buys the raw supplies used by the other departments.
            # self.production_team = [] # Physically makes the serum and sends it off to be sold.
            # self.hr_team = [] # Manages everyone else and improves effectiveness. Needed as company grows.

            self.head_researcher = None #A reference to the head researcher is stored here, for use in important events.
            self.company_model = None #A reference to the current company model. May be used for some events.

            self.max_employee_count = 5

            self.supply_count = 0
            self.supply_goal = 250
            self.auto_sell_threshold = None
            self.marketability = 0
            #self.production_points = 0 Use to be used to store partial progress on serum. is now stored in the assembly line array
            self.team_effectiveness = 100 #Ranges from 50 (Chaotic, everyone functions at 50% speed) to 200 (masterfully organized). Normal levels are 100, special traits needed to raise it higher.
            self.effectiveness_cap = 100 #Max cap, can be raised.

            self.research_tier = 0 #The tier of research the main character has unlocked with storyline events. 0 is starting, 3 is max.

            self.serum_designs = [] #Holds serum designs that you have researched.
            self.active_research_design = None #The current research (serum design or serum trait) the business is working on

            self.batch_size = 5 #How many serums are produced in each production batch
            self.production_lines = 2 #How many different production lines the player has access to.
            self.serum_production_array = {} #This dict will hold tuples of int(line number):[SerumDesign, int(weight), int(production points), int(autosell)]


            self.inventory = SerumInventory([])
            self.sale_inventory = SerumInventory([])

            #self.policy_list = [] #This is a list of Policy objects.
            #self.active_policy_list = [] #This is a list of currently active policies (vs just owned ones)

            self.message_list = [] #This list of strings is shown at the end of each day on the business update screen. Cleared each day.
            self.counted_message_list = {} #This is a dict holding the count of each message stored in it. Used when you want to have a message that is counted and the total shown at the end of the day.
            self.production_potential = 0 #How many production points the team was capable of
            self.supplies_purchased = 0
            self.production_used = 0 #How many production points were actually used to make something.
            self.research_produced = 0 #How much research the team produced today.
            self.sales_made = 0
            self.serums_sold = 0

            self.partial_clarity = 0.0 #Float used to store partial clarity produced by research until it can be given out as a full integer.

            self.sales_multipliers = [] #This list holds ["Source_type",multiplier_as_float]. The multiplier is applied to the value of serums when they are sold.
            # Only the most positive modifier of any source type is used. (This means a 1.0 modifier can be used to replace a negative modifier).


            self.mandatory_crises_list = [] #A list of crises to be resolved at the end of the turn, generally generated by events that have taken place.
            self.mandatory_morning_crises_list = [] #A list of specifically morning crises that need to be resolved.

            self.event_triggers_dict = {} #This dictionary will be used to hold flags for story events and triggers. In general a string is the key and a bool is the value stored.
            self.event_triggers_dict["policy_tutorial"] = 1 #We have a policy tutorial.
            self.event_triggers_dict["research_tutorial"] = 1 #We have a research tutorial.
            self.event_triggers_dict["design_tutorial"] = 1 #We have a serum design tutorial.
            self.event_triggers_dict["production_tutorial"] = 1 #We have a production tutorial.
            self.event_triggers_dict["outfit_tutorial"] = 1 #We have an outfit design tutorial.
            self.event_triggers_dict["hiring_tutorial"] = 1 #We have an outfit design tutorial.

            self.listener_system = Listener_Management_System()

        @property
        def active_policy_list(self):
            if not hasattr(self, "_active_policy_list"):
                self._active_policy_list = MappedList(Policy, all_policies_in_the_game)
            return self._active_policy_list

        @property
        def policy_list(self):
            if not hasattr(self, "_policy_list"):
                self._policy_list = MappedList(Policy, all_policies_in_the_game)
            return self._policy_list

        @property
        def m_div(self):
            if not hasattr(self, "_m_div"):
                self._m_div = None
            return next((x for x in list_of_places if x.identifier == self._m_div), None)

        @m_div.setter
        def m_div(self, value):
            if isinstance(value, Room):
                self._m_div = value.identifier

        @property
        def p_div(self):
            if not hasattr(self, "_p_div"):
                self._p_div = None
            return next((x for x in list_of_places if x.identifier == self._p_div), None)

        @p_div.setter
        def p_div(self, value):
            if isinstance(value, Room):
                self._p_div = value.identifier

        @property
        def r_div(self):
            if not hasattr(self, "_r_div"):
                self._r_div = None
            return next((x for x in list_of_places if x.identifier == self._r_div), None)

        @r_div.setter
        def r_div(self, value):
            if isinstance(value, Room):
                self._r_div = value.identifier

        @property
        def s_div(self):
            if not hasattr(self, "_s_div"):
                self._s_div = None
            return next((x for x in list_of_places if x.identifier == self._s_div), None)

        @s_div.setter
        def s_div(self, value):
            if isinstance(value, Room):
                self._s_div = value.identifier

        @property
        def h_div(self):
            if not hasattr(self, "_h_div"):
                self._h_div = None
            return next((x for x in list_of_places if x.identifier == self._h_div), None)

        @h_div.setter
        def h_div(self, value):
            if isinstance(value, Room):
                self._h_div = value.identifier

        @property
        def head_researcher(self):
            if not hasattr(self, "_head_researcher"):
                self._head_researcher = None
            return next((x for x in all_people_in_the_game() if x.identifier == self._head_researcher), None)

        @head_researcher.setter
        def head_researcher(self, value):
            if isinstance(value, Person):
                self._head_researcher = value.identifier
            else:
                self._head_researcher = None

        @property
        def company_model(self):
            if not hasattr(self, "_company_model"):
                self._company_model = None
            return next((x for x in all_people_in_the_game() if x.identifier == self._company_model), None)

        @company_model.setter
        def company_model(self, value):
            if isinstance(value, Person):
                self._company_model = value.identifier
            else:
                self._company_model = None

        @property
        def research_team(self):
            if not hasattr(self, "_research_team"):
                self._research_team = MappedList(Person, all_people_in_the_game)
            return self._research_team

        @property
        def market_team(self):
            if not hasattr(self, "_market_team"):
                self._market_team = MappedList(Person, all_people_in_the_game)
            return self._market_team

        @property
        def supply_team(self):
            if not hasattr(self, "_supply_team"):
                self._supply_team = MappedList(Person, all_people_in_the_game)
            return self._supply_team

        @property
        def production_team(self):
            if not hasattr(self, "_production_team"):
                self._production_team = MappedList(Person, all_people_in_the_game)
            return self._production_team

        @property
        def hr_team(self):
            if not hasattr(self, "_hr_team"):
                self._hr_team = MappedList(Person, all_people_in_the_game)
            return self._hr_team

        def run_turn(self): #Run each time the time segment changes. Most changes are done here.
            if time_of_day == 1 and daily_serum_dosage_policy.is_active() and self.is_work_day(): #Not done on run_day because we want it to apply at the _start_ of the day.
                self.give_daily_serum()

            #Compute efficiency drop Only people in the office lower effectiveness, no loss on weekends, not in for the day, etc.
            for person in [x for x in self.supply_team + self.research_team + self.production_team + self.market_team if x in self.s_div.people + self.r_div.people + self.p_div.people + self.m_div.people]:
                self.team_effectiveness -= 1 #TODO: Make this dependant on charisma (High charisma have a lower impact on effectiveness) and happiness.

            #Compute effiency rise from HR
            for person in [x for x in self.hr_team if x in self.h_div.people]:
                self.hr_progress(person.charisma,person.int,person.hr_skill)
                person.change_happiness(person.get_opinion_score("working")+person.get_opinion_score("HR work"), add_to_log = False)

            if self.team_effectiveness < 50:
                self.team_effectiveness = 50

            if self.team_effectiveness > self.effectiveness_cap:
                self.team_effectiveness = self.effectiveness_cap

            #Compute other deparement effects
            for person in [x for x in self.supply_team if x in self.s_div.people]:
                self.supply_purchase(person.focus,person.charisma,person.supply_skill)
                person.change_happiness(person.get_opinion_score("working")+person.get_opinion_score("supply work"), add_to_log = False)

            for person in [x for x in self.research_team if x in self.r_div.people]:
                self.research_progress(person.int,person.focus,person.research_skill)
                person.change_happiness(person.get_opinion_score("working")+person.get_opinion_score("research work"), add_to_log = False)

            for person in [x for x in self.production_team if x in self.p_div.people]:
                self.production_progress(person.focus,person.int,person.production_skill)
                person.change_happiness(person.get_opinion_score("working")+person.get_opinion_score("production work"), add_to_log = False)

            self.mark_autosale() #Mark extra serums to be sold by marketing.

            for person in [x for x in self.market_team if x in self.m_div.people]:
                if person.should_wear_uniform():
                    self.sale_progress(person.charisma,person.focus, person.market_skill, slut_modifier = person.outfit.slut_requirement) #If there is a uniform pass it's sluttiness along.
                else:
                    self.sale_progress(person.charisma, person.focus, person.market_skill) #Otherwise their standard outfit provides no bonuses.
                person.change_happiness(person.get_opinion_score("working")+person.get_opinion_score("marketing work"), add_to_log = False)

            for policy in self.active_policy_list:
                policy.on_turn()

        def run_move(self):
            for policy in self.active_policy_list:
                policy.on_move()



        def run_day(self): #Run at the end of the day.
            #Pay everyone for the day
            if self.is_work_day():
                cost = self.calculate_salary_cost()
                self.funds += -cost

                for policy in self.active_policy_list:
                    policy.on_day()
            return

        def is_open_for_business(self): #Checks to see if employees are currently working
            if not self.is_work_day(): #It is the weekend, people have the day off.
                return False

            elif time_of_day == 1 or time_of_day == 2 or time_of_day == 3: #It is the work period of the day
                return True

            return False #If all else fails, give them some time off.

        def is_work_day(self):
            if day % 7 == 5 or day % 7 == 6: #TODO: add support for expanding workdays
                return False
            return True

        def is_weekend(self):#TODO: add support for expanding/changing the weekend
            if day % 7 == 5 or day % 7 == 6: #Checks to see if it is saturday or sunday. Note that days might eventually be both neither weekend or workday, or both weekend AND workday!
                return True
            return False

        def get_uniform_wardrobe(self,title): #Takes a title and returns the correct uniform for that division, if one exists. If it is None, returns false. TODO: get this working.
            if title == "Marketing":
                return self.m_uniform.merge_wardrobes(self.all_uniform)
            elif title == "Researcher":
                return self.r_uniform.merge_wardrobes(self.all_uniform)
            elif title == "Production":
                return self.p_uniform.merge_wardrobes(self.all_uniform)
            elif title == "Supply":
                return self.s_uniform.merge_wardrobes(self.all_uniform)
            elif title == "Human Resources":
                return self.h_uniform.merge_wardrobes(self.all_uniform)
            else:
                return None

        def get_uniform_wardrobe_for_person(self, the_person):
            return self.get_uniform_wardrobe(self.get_employee_title(the_person))

        def get_uniform_limits(self): #Returns three values: the max sluttiness of a full outfit, max sluttiness of an underwear set, and if only overwear sets are allowed or notself.
            slut_limit = 0
            underwear_limit = 0
            limited_to_top = True
            if maximal_arousal_uniform_policy.is_active():
                slut_limit = 999 #ie. no limit at all.
                underwear_limit = 999
                limited_to_top = False
            elif corporate_enforced_nudity_policy.is_active():
                slut_limit = 80
                underwear_limit = 999
                limited_to_top = False
            elif minimal_coverage_uniform_policy.is_active():
                slut_limit = 60
                underwear_limit = 15
                limited_to_top = False
            elif reduced_coverage_uniform_policy.is_active():
                slut_limit = 40
                underwear_limit = 10
                limited_to_top = False
            elif casual_uniform_policy.is_active():
                slut_limit = 25
                underwear_limit = 0
                limited_to_top = True
            elif relaxed_uniform_policy.is_active():
                slut_limit = 15
                underwear_limit = 0
                limited_to_top = True
            elif strict_uniform_policy.is_active():
                slut_limit = 5
                underwear_limit = 0
                limited_to_top = True
            else:
                slut_limit = 0
                underwear_limit = 0
                limited_to_top = True
            return slut_limit, underwear_limit, limited_to_top

        def clear_messages(self): #clear all messages for the day.
            self.message_list = []
            self.counted_message_list = {}
            self.production_potential = 0
            self.supplies_purchased = 0
            self.production_used = 0
            self.research_produced = 0
            self.sales_made = 0
            self.serums_sold =0

        def add_counted_message(self,message,new_count):
            if message in self.counted_message_list:
                self.counted_message_list[message] += new_count
            else:
                self.counted_message_list[message] = new_count

        def add_normal_message(self,message): #Adds an uncounted message, only ever listed once per day
            if message not in self.message_list:
                self.message_list.append(message)

        def calculate_salary_cost(self):
            daily_cost = 0
            for person in self.supply_team + self.research_team + self.production_team + self.market_team + self.hr_team:
                daily_cost += person.salary
            return daily_cost

        def add_serum_design(self,the_serum):
            self.serum_designs.append(the_serum)

        def remove_serum_design(self,the_serum):
            self.serum_designs.remove(the_serum)
            if the_serum is self.active_research_design:
                self.active_research_design = None

            delete_list = []
            for line in self.serum_production_array:
                if the_serum is self.serum_production_array[line][0]:
                    delete_list.append(line) #Store a list of all the keys we need to delete to avoid modifying while interating. Needed in case two lines are making the same serum.

            for key in delete_list: #Now delete the production lines.
                del self.serum_production_array[key]

        def set_serum_research(self,new_research):
            self.active_research_design = new_research

        def research_progress(self,int,focus,skill):
            research_amount = ((3*int) + (focus) + (2*skill) + 10) * (self.team_effectiveness / 100.0)

            if self.head_researcher:
                bonus_percent = (self.head_researcher.int - 2)*0.05
                research_amount = research_amount * (1.0 + bonus_percent) #Every point above int 2 gives a 5% bonus.
                if bonus_percent > 0:
                    self.add_normal_message("Head researcher " + self.head_researcher.title + "'s intelligence resulted in a " + str(bonus_percent*100) + "% increase in research produced!")
                else:
                    self.add_normal_message("Head researcher " + self.head_researcher.title + "'s intelligence resulted in a " + str(bonus_percent*100) + "% change in research produced.")
            else:
                research_amount = research_amount * 0.9 #No head researcher is treated like int 0.
                self.add_normal_message("No head researcher resulted in a 10% reduction in research produced! Assign a head researcher at R&D!")

            research_amount = __builtin__.int( research_amount ) # round off values

            if self.active_research_design is not None:
                the_research = self.active_research_design
                is_researched = the_research.researched # If it was researched before we added any research then we are increasing the mastery level of a trait (does nothing to serum designs)
                self.research_produced += research_amount
                if the_research.add_research(research_amount): #Returns true if the research is completed by this amount'
                    if isinstance(the_research, SerumDesign):
                        the_research.generate_side_effects() #The serum will generate any side effects that are needed.
                        self.mandatory_crises_list.append(Action("Research Finished Crisis",serum_creation_crisis_requirement,"serum_creation_crisis_label",the_research)) #Create a serum finished crisis, it will trigger at the end of the round
                        self.add_normal_message("New serum design researched: " + the_research.name)
                        self.active_research_design = None
                    elif isinstance(the_research, SerumTrait):
                        if is_researched: #We've reseached it already, increase mastery level instead.
                            self.add_normal_message("Serum trait mastery improved: " + the_research.name + ", Now " + str(the_research.mastery_level))
                        else:
                            self.add_normal_message("New serum trait researched: " + the_research.name)
                            self.active_research_design = None #If it's a newly discovered trait clear it so we don't start mastering it without player input.

            else:
                clarity_produced = 0
                if theoretical_research.is_active():
                    clarity_produced += research_amount * 0.05

                if research_journal_subscription.is_active():
                    clarity_produced += research_amount * 0.05

                if independent_experimentation.is_active():
                    if mc.business.supply_count >= 5:
                        mc.business.supply_count += -5
                        clarity_produced += research_amount * 0.05

                self.partial_clarity += clarity_produced
                if self.partial_clarity >= 1.0:
                    int_clarity = int(self.partial_clarity)
                    self.partial_clarity += -int_clarity
                    mc.add_clarity(int_clarity, add_to_log = False)
                    self.add_counted_message("Idle R&D team produced Clarity")




                #research_amount = 0 #We didn't actually research anything because there is nothing to research!

            return research_amount

        def player_research(self):
            amount_researched = self.research_progress(mc.int,mc.focus,mc.research_skill)
            self.listener_system.fire_event("general_work")
            self.listener_system.fire_event("player_research", amount = amount_researched)
            renpy.say(None,"You spend time in the lab, experimenting with different chemicals and techniques and producing " + str(amount_researched) + " research points.")
            return amount_researched

        def player_buy_supplies(self):
            amount_bought = self.supply_purchase(mc.focus,mc.charisma,mc.supply_skill)
            self.listener_system.fire_event("general_work")
            self.listener_system.fire_event("player_supply_purchase", amount = amount_bought)
            renpy.say(None,"You spend time securing new supplies for the lab, purchasing " + str(amount_bought) + " units of serum supplies.")
            return amount_bought

        def supply_purchase(self,focus,cha,skill):
            max_supply = __builtin__.int( ((3*focus) + (cha) + (2*skill) + 10) * (self.team_effectiveness / 100.0) )
            max_supply = int(max_supply)
            if max_supply + self.supply_count > self.supply_goal:
                max_supply = self.supply_goal - self.supply_count
                if max_supply <= 0:
                    return 0

            self.funds += -max_supply
            self.supply_count += max_supply
            self.supplies_purchased += max_supply #Used for end of day reporting
            return max_supply

        def player_market(self):
            amount_sold = self.sale_progress(mc.charisma,mc.focus,mc.market_skill)
            self.listener_system.fire_event("player_serums_sold_count", amount = amount_sold)
            self.listener_system.fire_event("general_work")
            renpy.say(None,"You spend time making phone calls to clients and shipping out orders. You sell " + str(amount_sold) + " doses of serum.")
            return amount_sold

        def sale_progress(self,cha,focus,skill, slut_modifier = 0):

            serum_value_multiplier = 1.00 #For use with value boosting policies. Multipliers are multiplicative.
            if male_focused_marketing_policy.is_active(): #Increase value by the character's outfit sluttiness if you own that policy.
                sluttiness_multiplier = (slut_modifier/100.0) + 1
                serum_value_multiplier = serum_value_multiplier * (sluttiness_multiplier)

            multipliers_used = {} #Generate a dict with only the current max multipliers of each category.
            for multiplier_source in self.sales_multipliers:
                if not multiplier_source[0] in multipliers_used:
                    multipliers_used[multiplier_source[0]] = multiplier_source[1]
                elif multiplier_source[1] > multipliers_used.get(multiplier_source[0]):
                    multipliers_used[multiplier_source[0]] = multiplier_source[1]

            for maxed_multiplier in multipliers_used:
                value_change = multipliers_used.get(maxed_multiplier)
                serum_value_multiplier = serum_value_multiplier * value_change
                if value_change > 1:
                    self.add_normal_message("+" + str((value_change-1)*100) + "% serum value due to " + maxed_multiplier + ".")
                elif value_change < 1: #No message shown for exactly 1.
                    self.add_normal_message(str((value_change-1)*100) + "% serum value due to " + maxed_multiplier + ".") #Duplicate normal messages are not shown twice, so this should only exist once per turn, per multiplier.

            #Total number of doses of serum that can be sold by this person.
            serum_sale_count = __builtin__.int( ((3 * cha) + focus + (2 * skill) + 5) * (self.team_effectiveness / 100.0) )
            sorted_by_value = sorted(self.sale_inventory.serums_held, key = lambda serum: serum[0].value) #List of tuples [SerumDesign, count], sorted by the value of each design. Used so most valuable serums are sold first.
            if self.sale_inventory.get_any_serum_count() < serum_sale_count:
                serum_sale_count = self.sale_inventory.get_any_serum_count()

            this_batch_serums_sold = 0
            if serum_sale_count > 0: #ie. we have serum in our inventory to sell, and the capability to sell them.
                for serum in sorted_by_value:
                    if serum_sale_count <= serum[1]:
                        #There are enough to satisfy order. Remove, add value to wallet, and break
                        value_sold = serum_sale_count * serum[0].value * serum_value_multiplier
                        if value_sold < 0:
                            value_sold = 0
                        self.funds += value_sold
                        self.sales_made += value_sold
                        self.listener_system.fire_event("serums_sold_value", amount = value_sold)
                        self.serums_sold += serum_sale_count
                        this_batch_serums_sold += serum_sale_count
                        self.sale_inventory.change_serum(serum[0],-serum_sale_count)
                        serum_sale_count = 0
                        break
                    else:
                        #There are not enough in this single order, remove _all_ of them, add value, go onto next thing.
                        serum_sale_count += -serum[1] #We were able to sell this number of serum.
                        value_sold = serum[1] * serum[0].value * serum_value_multiplier
                        if value_sold < 0:
                            value_sold = 0
                        self.funds += value_sold
                        self.sales_made += value_sold
                        self.listener_system.fire_event("serums_sold_value", amount = value_sold)
                        self.serums_sold += serum_sale_count
                        this_batch_serums_sold += serum_sale_count
                        self.sale_inventory.change_serum(serum[0],-serum[1]) #Should set serum count to 0.
                        #Don't break, we haven't used up all of the serum count
            return this_batch_serums_sold



        def production_progress(self,focus,int,skill):
            #First, figure out how many production points we can produce total. Subtract that much supply and mark that much production down for the end of day report.
            production_amount = __builtin__.int( ((3*focus) + (int) + (2*skill) + 10) * (self.team_effectiveness / 100.0) )
            self.production_potential += production_amount

            if self.serum_production_array is None:
                return #If we don't have anything in production just tally how much we could have produced and move on.

            if production_amount > self.supply_count:
                production_amount = self.supply_count #Figure out our total available production, before we split it up between tasks (which might not have 100% usage!)

            #Now go through each production line we have marked.
            for production_line in self.serum_production_array:
                # A production line is a tuple of [SerumDesign, production weight (int), production point progress (int)].
                serum_weight = self.serum_production_array[production_line][1]
                the_serum = self.serum_production_array[production_line][0]

                proportional_production = (serum_weight/100.0) * production_amount #Get the closest integer value for the weighted production we put into the serum
                self.production_used += proportional_production #Update our usage stats and subract supply needed.
                self.supply_count += -proportional_production

                self.serum_production_array[production_line][2] += proportional_production
                serum_prod_cost = the_serum.production_cost
                if serum_prod_cost <= 0:
                    serum_prod_cost = 1
                serum_count = self.serum_production_array[production_line][2]//serum_prod_cost #Calculates the number of batches we have made (previously for individual serums, now for entire batches)
                if serum_count > 0:
                    self.add_counted_message("Produced " + self.serum_production_array[production_line][0].name,serum_count*self.batch_size) #Give a note to the player on the end of day screen for how many we made.
                    self.serum_production_array[production_line][2] -= serum_count * self.serum_production_array[production_line][0].production_cost
                    self.inventory.change_serum(self.serum_production_array[production_line][0],serum_count*self.batch_size) #Add the number serums we made to our inventory.

            return production_amount

        def change_production(self,new_serum,production_line):
            if production_line in self.serum_production_array: #If it already exists, change the serum type and production points stored, but keep the weight for that line (it can be changed later)
                self.serum_production_array[production_line][0] = new_serum
                self.serum_production_array[production_line][1] = int(100 - self.get_used_line_weight() + self.serum_production_array[production_line][1]) #Set the production weight to everything we have remaining
                self.serum_production_array[production_line][2] = 0 #Set production points stored to 0 for the new serum
                self.serum_production_array[production_line][3] = -1 #Set autosell to -1, ie. don't auto sell.
            else: #If the production line didn't exist before, add a key for that line.
                self.serum_production_array[production_line] = [new_serum, int(100 - self.get_used_line_weight()), 0, -1]

        def get_used_line_weight(self):
            used_production = 0
            for existing_lines in self.serum_production_array:
                used_production += self.serum_production_array[existing_lines][1] #Tally how much weight we are using so far.
            return used_production

        def change_line_weight(self,line,weight_change):
            if line in self.serum_production_array:
                used_production = self.get_used_line_weight()
                if weight_change > 0 and weight_change + used_production > 100:
                    weight_change = 100 - used_production #If the full weight change would put us above our 100% max cap it at as much as can be assigned.

                self.serum_production_array[line][1] += weight_change
                if self.serum_production_array[line][1] < 0:
                    self.serum_production_array[line][1] = 0 #We cannot have a value less than 0%

        def change_line_autosell(self, line, threshold_change):
            if line in self.serum_production_array:
                if threshold_change > 0 and self.serum_production_array[line][3] < 0: #We use negative values as a marker for no threshold. If it's negative always treat it as -1 when we start adding again.
                    self.serum_production_array[line][3] = -1
                self.serum_production_array[line][3] += threshold_change

        def mark_autosale(self):
            for line in self.serum_production_array:
                if self.serum_production_array[line][3] >= 0: #There is an auto sell threshold set.
                    if self.inventory.get_serum_count(self.serum_production_array[line][0]) > self.serum_production_array[line][3]:
                        difference = int(self.inventory.get_serum_count(self.serum_production_array[line][0]) - self.serum_production_array[line][3]) #Check how many serums we need to sell to bring us to the threshold.
                        self.inventory.change_serum(self.serum_production_array[line][0], -difference) #Remove them from the production inventory.
                        self.sale_inventory.change_serum(self.serum_production_array[line][0], difference) #Add them to the sales inventory.

        def get_random_weighed_production_serum(self): #Return the serum design of one of our activly produced serums, relative probability by weight.
            used_production = 0
            for key in self.serum_production_array:
                used_production += self.serum_production_array[key][1] #Sum how much production we are using, usually 100%
            if used_production == 0:
                return None #If we are not _actually_ producing anything, return None.

            random_serum_number = renpy.random.randint(0,used_production)
            for key in self.serum_production_array:
                if random_serum_number <= self.serum_production_array[key][1]:
                    return self.serum_production_array[key][0]
                else:
                    random_serum_number -= self.serum_production_array[key][1] #Subtract the probability of this one from our number to make progress in our search.




        def player_production(self):
            production_amount = self.production_progress(mc.focus,mc.int,mc.production_skill)
            self.listener_system.fire_event("player_production", amount = production_amount)
            self.listener_system.fire_event("general_work")
            renpy.say(None,"You spend time in the lab synthesizing serum from the it's raw chemical precursors. You generate " + str(production_amount) + " production points.")
            return production_amount

        def player_hr(self):
            eff_amount = self.hr_progress(mc.charisma,mc.int,mc.hr_skill)
            self.listener_system.fire_event("player_efficiency_restore", amount = eff_amount)
            self.listener_system.fire_event("general_work")
            renpy.say(None,"You settle in and spend a few hours filling out paperwork, raising company efficiency by " + str(eff_amount )+ "%%.")
            return eff_amount

        def hr_progress(self,cha,int,skill): #Don't compute efficiency cap here so that player HR effort will be applied against any efficiency drop even though it's run before the rest of the end of the turn.
            restore_amount = (3*cha) + (int) + (2*skill) + 5
            self.team_effectiveness += restore_amount
            return restore_amount

        def change_team_effectiveness(self, the_amount):
            self.team_effectiveness += the_amount
            if self.team_effectiveness > self.effectiveness_cap:
                self.team_effectiveness = self.effectiveness_cap
            elif self.team_effectiveness < 50:
                self.team_effectiveness = 50

        def update_employee_status(self, person):
            if person.event_triggers_dict.get("employed_since", -1) == -1:
                person.event_triggers_dict["employed_since"] = day
                self.listener_system.fire_event("new_hire", the_person = person)

            for other_employee in self.get_employee_list():
                town_relationships.begin_relationship(person, other_employee) #They are introduced to everyone at work, with a starting value of "Acquaintance"

        def move_person_to_division(self, person, division):
            if not person in division.people:
                if person in person.location.people:
                    person.location.move_person(person, division)
                else:
                    division.add_person(person)

        def add_employee_research(self, person, add_to_location = False):
            if add_to_location:
                self.move_person_to_division(person, self.r_div)
            if not person in self.research_team:
                self.research_team.append(person)
            if not employee_role in person.special_role:
                person.special_role.append(employee_role)
            person.job = self.get_employee_title(person)
            person.set_work(self.r_div)
            self.update_employee_status(person)

        def add_employee_production(self, person, add_to_location = False):
            if add_to_location:
                self.move_person_to_division(person, self.p_div)
            if not person in self.production_team:
                self.production_team.append(person)
            if not employee_role in person.special_role:
                person.special_role.append(employee_role)
            person.job = self.get_employee_title(person)
            person.set_work(self.p_div)
            self.update_employee_status(person)

        def add_employee_supply(self, person, add_to_location = False):
            if add_to_location:
                self.move_person_to_division(person, self.s_div)
            if not person in self.supply_team:
                self.supply_team.append(person)
            if not employee_role in person.special_role:
                person.special_role.append(employee_role)
            person.job = self.get_employee_title(person)
            person.set_work(self.s_div)
            self.update_employee_status(person)

        def add_employee_marketing(self, person, add_to_location = False):
            if add_to_location:
                self.move_person_to_division(person, self.m_div)
            if not person in self.market_team:
                self.market_team.append(person)
            if not employee_role in person.special_role:
                person.special_role.append(employee_role)
            person.job = self.get_employee_title(person)
            person.set_work(self.m_div)
            self.update_employee_status(person)

        def add_employee_hr(self, person, add_to_location = False):
            if add_to_location:
                self.move_person_to_division(person, self.h_div)
            if not person in self.hr_team:
                self.hr_team.append(person)
            if not employee_role in person.special_role:
                person.special_role.append(employee_role)
            person.job = self.get_employee_title(person)
            person.set_work(self.h_div)
            self.update_employee_status(person)

        def remove_employee(self, person, remove_linked = True):
            if person in self.research_team:
                self.research_team.remove(person)
            if person in self.production_team:
                self.production_team.remove(person)
            if person in self.supply_team:
                self.supply_team.remove(person)
            if person in self.market_team:
                self.market_team.remove(person)
            if person in self.hr_team:
                self.hr_team.remove(person)

            person.set_work(None)

            person.remove_role(employee_role, remove_linked = remove_linked)

            if person is self.head_researcher:
                self.fire_head_researcher()

            if person is self.company_model:
                self.fire_company_model()

            self.listener_system.fire_event("fire_employee", the_person = person)

        def get_employee_list(self):
            return self.research_team + self.production_team + self.supply_team + self.market_team + self.hr_team

        def get_employee_count(self):
            return len(self.get_employee_list())

        def get_max_employee_slut(self):
            max = -1 #Set to -1 for an empty business, all calls should require at least sluttiness 0
            for person in self.get_employee_list():
                if person.sluttiness > max:
                    max = person.sluttiness
            return max

        def get_employee_title(self, the_person):
            if the_person in self.research_team:
                return "Researcher"

            elif the_person in self.market_team:
                return "Marketing"

            elif the_person in self.supply_team:
                return "Supply"

            elif the_person in self.production_team:
                return "Production"

            elif the_person in self.hr_team:
                return "Human Resources"
            else:
                return "None"

        def get_employee_workstation(self, the_person): #Returns the location a girl should be working at, or "None" if the girl does not work for you
            if the_person in self.research_team:
                return self.r_div

            elif the_person in self.market_team:
                return self.m_div

            elif the_person in self.supply_team:
                return self.s_div

            elif the_person in self.production_team:
                return self.p_div

            elif the_person in self.hr_team:
                return self.h_div
            else:
                return None

        def get_requirement_employee_list(self, exclude_list = None, **kargs): #Get a list of employees who pass the validrequirements. Pass the same arguments as person_meets_requirements expects as named args.
            employees_meeting_requirement = []
            if exclude_list is None:
                exclude_list = []
            for person in self.get_employee_list():
                if person not in exclude_list:
                    if person.person_meets_requirements(**kargs):
                        employees_meeting_requirement.append(person)
            return employees_meeting_requirement

        def give_daily_serum(self):
            if self.r_serum:
                the_serum = self.r_serum
                for person in self.research_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum), add_to_log = False) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of " + the_serum.name + " to give to the research division."
                        if not the_message in self.message_list:
                            self.add_normal_message(the_message)

            if self.m_serum:
                the_serum = self.m_serum
                for person in self.market_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum), add_to_log = False) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of " + the_serum.name + " to give to the marketing division."
                        if not the_message in self.message_list:
                            self.add_normal_message(the_message)

            if self.p_serum:
                the_serum = self.p_serum
                for person in self.production_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum), add_to_log = False) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of " + the_serum.name + " to give to the production division."
                        if not the_message in self.message_list:
                            self.add_normal_message(the_message)

            if self.s_serum:
                the_serum = self.s_serum
                for person in self.supply_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum), add_to_log = False) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of " + the_serum.name + " to give to the supply procurement division."
                        if not the_message in self.message_list:
                            self.add_normal_message(the_message)

            if self.h_serum:
                the_serum = self.h_serum
                for person in self.hr_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum), add_to_log = False) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of " + the_serum.name + " to give to the human resources division."
                        if not the_message in self.message_list:
                            self.add_normal_message(the_message)

        def advance_tutorial(self, tutorial_name):
            self.event_triggers_dict[tutorial_name] += 1 #advance our tutorial slot.

        def reset_tutorial(self, tutorial_name):
            self.event_triggers_dict[tutorial_name] = 1 #Reset it when the reset tutorial button is used.

        def add_sales_multiplier(self, multiplier_class, multiplier):
            mc.log_event("Serum sale value increased by " + str((multiplier - 1) * 100) + "% due to " + multiplier_class + ".", "float_text_grey")
            self.sales_multipliers.append([multiplier_class, multiplier])

        def remove_sales_multiplier(self, multiplier_class, multiplier):
            if [multiplier_class, multiplier] in self.sales_multipliers:
                mc.log_event("No longer receiving " + str((multiplier - 1) * 100) + "% serum value increase from " + multiplier_class + ".", "float_text_grey")
                self.sales_multipliers.remove([multiplier_class, multiplier])

        def hire_company_model(self, person):
            if self.company_model:
                self.fire_company_model()
            self.company_model = person
            person.special_role.append(company_model_role)

        def fire_company_model(self):
            if self.company_model:
                self.company_model.special_role.remove(company_model_role)
                self.company_model = None

        def hire_head_researcher(self, person):
            if self.head_researcher:
                self.fire_head_researcher()
            self.head_researcher = person
            person.special_role.append(head_researcher)

        def fire_head_researcher(self):
            if self.head_researcher:
                self.head_researcher.special_role.remove(head_researcher)
                self.head_researcher = None
