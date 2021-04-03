init 0 python:
    ## Organisation Policies ##
    organisation_policies_list = []


    def increase_max_employee_size(amount):
        mc.business.max_employee_count += amount

    def business_size_1_requirement():
        return True

    business_size_1_policy = Policy(name = "Employee Count Improvement One",
        desc = "Some basic employee management and tracking software will let you hire more employees. Increases max employee count by 2.",
        cost = 500,
        toggleable = False,
        requirement = business_size_1_requirement,
        on_buy_function = increase_max_employee_size,
        extra_arguments = {"amount":2})
    organisation_policies_list.append(business_size_1_policy)

    def business_size_2_requirement():
        if business_size_1_policy.is_owned():
            return True
        else:
            return False

    business_size_2_policy = Policy(name = "Employee Count Improvement Two",
        desc = "Improved employee management software yet again increases the number of employees you can comfortably keep around. Increases max employee count by 3.",
        cost = 2000,
        toggleable = False,
        requirement = business_size_2_requirement,
        on_buy_function = increase_max_employee_size,
        extra_arguments = {"amount":3})
    organisation_policies_list.append(business_size_2_policy)

    def business_size_3_requirement():
        if business_size_2_policy.is_owned():
            return True
        else:
            return False

    business_size_3_policy = Policy(name = "Employee Count Improvement Three",
        desc = "Distributed management roles lets you nearly double the employee count of your business. Increases max employee count by 8.",
        cost = 5000,
        toggleable = False,
        requirement = business_size_3_requirement,
        on_buy_function = increase_max_employee_size,
        extra_arguments = {"amount":8})
    organisation_policies_list.append(business_size_3_policy)

    def business_size_4_requirement():
        if business_size_3_policy.is_owned():
            return True
        else:
            return False

    business_size_4_policy = Policy(name = "Employee Count Improvement Four",
        desc = "Fully automated payroll calculations, benefit management, and productivity tracking allows for a final, massive jump in maximum business size. Increases max employee count by 20.",
        cost = 10000,
        toggleable = False,
        requirement = business_size_4_requirement,
        on_buy_function = increase_max_employee_size,
        extra_arguments = {"amount":20})
    organisation_policies_list.append(business_size_4_policy)

    def public_advertising_license_requirement():
        return True

    public_advertising_license_policy = Policy(name = "Public Advertising License",
        desc = "After filling out the proper paperwork and familiarizing yourself with publishing regulations you will be ready to advertise your product in print publications. Allows you to pick a girl as your company model and launch ad campaigns.",
        cost = 2500,
        toggleable = False,
        requirement = public_advertising_license_requirement)

    organisation_policies_list.append(public_advertising_license_policy)

    def office_punishment_policy_requirement():
        return True

    office_punishment = Policy(name = "Office Punishment",
        desc = "Establish a formal set of punishments for business policy violations. Allows you to punish employees for infractions they have committed. More severe infractions enable more severe punishments.",
        cost = 700,
        toggleable = False,
        requirement = office_punishment_policy_requirement)
    organisation_policies_list.append(office_punishment)

    def corporal_punishment_policy_requirement():
        if office_punishment.is_owned():
            return True
        else:
            return False

    corporal_punishment = Policy(name = "Corporal Punishment",
        desc = "Updates to the company punishment guidelines allow for punishments involving physical contact. Research into the topic has shown sexual punishment to be extremely effective in cases of severe disobedience.",
        cost = 2000,
        toggleable = False,
        requirement = corporal_punishment_policy_requirement)
    organisation_policies_list.append(corporal_punishment)

    def strict_enforcement_policy_requirment():
        if office_punishment.is_owned():
            return True
        else:
            return False

    def strict_enforcement_on_day():
        mc.business.change_team_effectiveness(-1*mc.business.get_employee_count())

    strict_enforcement = Policy(name = "Strict Enforcement",
        desc = "By strictly applying the letter, rather than spirit, of the company punishment guidelines you are able to treat infractions as more severe than they initially seem. All infraction severities are increased by one while this policy is active, but the increased administrative work lowers business efficency by one per employee every day.",
        cost = 2500,
        toggleable = True,
        requirement = strict_enforcement_policy_requirment,
        on_day_function = strict_enforcement_on_day)
    organisation_policies_list.append(strict_enforcement)

    def draconian_enforcement_policy_requirement():
        if strict_enforcement.is_owned():
            return True
        else:
            return False

    def draconian_enforcement_on_day():
        for employee in mc.business.get_employee_list():
            employee.change_happiness(-5, add_to_log = False)

    draconian_enforcement = Policy(name = "Draconian Enforcement",
        desc = "Each policy infraction is to be punished to the utmost tolerable. All infraction severities are increased by one, but the restrictive office environment affects company morale, lowering all empolyee happiness by -5 per day.",
        cost = 5000,
        toggleable = True,
        requirement = draconian_enforcement_policy_requirement,
        on_day_function = draconian_enforcement_on_day,
        dependant_policies = strict_enforcement)
    organisation_policies_list.append(draconian_enforcement)

    def bureaucratic_nightmare_policy_requirement():
        if office_punishment.is_owned():
            return True
        else:
            return False

    def bureaucratic_nightmare_on_day():
        mc.business.change_team_effectiveness(-1*mc.business.get_employee_count())

    bureaucratic_nightmare = Policy(name = "Bureaucratic Nightmare",
        desc = "Rewriting all company policies to be intentionally vague and misleading creates a work environment where mistakes are practically unavoidable. Allows you to generate minor infractions at will, but the new labyrinthian rules result in business efficency dropping by an additional one per employee each day.",
        cost = 2500,
        toggleable = True,
        requirement = bureaucratic_nightmare_policy_requirement,
        on_day_function = bureaucratic_nightmare_on_day)
    organisation_policies_list.append(bureaucratic_nightmare)

    def theoretical_research_policy_requirement():
        return True

    theoretical_research = Policy(name = "Theoretical Research",
        desc = "Establish a framework that will allow your R&D team to contribute to the discovery of completely novel serum traits. When not given a specific task your research team will convert 5% of their generated Research Points into Clarity.",
        cost = 300,
        toggleable = False,
        requirement = theoretical_research_policy_requirement)
    organisation_policies_list.append(theoretical_research)

    def research_journal_subscription_requirement():
        if theoretical_research.is_owned():
            return True
        else:
            return False

    def research_journal_subscription_on_day():
        if mc.business.is_work_day():
            mc.businss.funds += -30

    research_journal_subscription = Policy(name = "Research Journal Subscription",
        desc = "Ensuring your research team has access to all of the latest research isn't cheap, but it is important if you want to push your own progress further and faster. Converts an additional 5% of idle Research Points into Clarity when your R&D team is idle. Costs $30 a day to maintain your subscription.",
        cost = 1000,
        toggleable = False,
        requirement = research_journal_subscription_requirement,
        on_day_function = research_journal_subscription_on_day)
    organisation_policies_list.append(research_journal_subscription)

    def independent_experimentation_requirement():
        if theoretical_research.is_owned():
            return True
        else:
            return False

    independent_experimentation = Policy(name = "Independent Experimentation",
        desc = "Make the lab available to your research staff and encourage them to pursue their own experiments when it would otherwise be idle. Requires 5 serum supply per researcher and converts an additional 5% of idle research production into Clarity.",
        cost = 500,
        toggleable = True,
        requirement = theoretical_research_policy_requirement)
    organisation_policies_list.append(independent_experimentation)
