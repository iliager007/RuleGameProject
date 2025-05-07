init python:
    class Rule:
        def __init__(self, condition, description, code):
            self.condition = condition
            self.description = description
            self.code = code

    def check_rules(zone):
        for rule in zone_rules[zone]:
            if rule.condition():
                return rule
        return None

    def start_zone_timer(seconds):
        if not timer_active:
            store.timer_active = True
            store.timer_triggered = False
            renpy.invoke_in_thread(zone_timer, seconds)

    def zone_timer(seconds):
        import time
        time.sleep(seconds)
        store.timer_triggered = True
        rule = check_rules(store.current_zone)
        if rule:
            store.death_rule = rule
            renpy.jump("death")
    
    def is_rule_known(rule):
        for known_rule in rule_database:
            if known_rule.code == rule.code:
                return True
        return False

    def hide_all_screens():
        renpy.hide_screen("zone0_objects")
        renpy.hide_screen("rule_database")

        
#overall
default rule_database = []
default first_death = True
default current_zone = "zone0"
default death_rule = None

#zone0
default clicked_red = False
#zone1
default timer_active = False
default on_table = False
default timer_triggered = False
#zone2
default asked_about_experiment = False
default asked_about_lab = False
default asked_about_time = False
default asked_about_village = False
default examined_body = False
default understood_npc_nature = False
default saw_footprints = False
default fetched_water_at_night = False
default failed_solve = False

#Characters
#zone2
define villager1 = Character("Деревенский житель", color="#8bc34a")
define villager2 = Character("Деревенский житель", color="#ff9800")
define mayor = Character("Староста", color="#795548")


define zone_rules = {
    "zone0": [
        Rule(
            condition=lambda: clicked_red, 
            description="Не трогать красные объекты",
            code="0x1F"
        )
    ],
    "zone1": [
        Rule(
            condition=lambda: timer_triggered and not on_table,
            description="После гонга нельзя стоять на полу",
            code="0x2A"
        )
    ], 
    "zone2": [
        Rule(
            condition=lambda: failed_solve,
            description="Загадка должна быть решена",
            code="0x3B"
        ),
        Rule(
            condition=lambda: fetched_water_at_night,
            description="Не набирать воду ночью",
            code="0x3I"
        )
    ]
}

label start:
    scene black
    
    "Вы приходите в себя в холодном металлическом помещении..."
    
    jump zone_controller

label zone_controller:
    $ hide_all_screens()
    call expression current_zone from _call_expression
    return

label zone0:
    scene bg_room
    show screen zone0_objects
    
    "Вы находитесь в зоне 0. Перед вами красная кнопка и дверь. На двери неизвестный вам знак."
    
    menu:
        "Нажать красную кнопку":
            $ clicked_red = True
            $ rule = check_rules(current_zone)
            if rule:
                $ death_rule = rule
                jump death
            else:
                "Кнопка нажата, но ничего не произошло."
            
        "Открыть дверь":
            $ current_zone = "zone1"
            "Вы переходите в следующую зону..."
            jump zone_controller
    
    jump zone0

label zone1:
    scene bg_lab
    $ start_zone_timer(10)
    
    "Вы в зоне 1. В углу стоит металлический стол, а на стене висит динамик, в конце комнаты находится дверь. На двери был знак, такой же как вы видели в прошлой комнате."

    "Из динамика донеслось что-то похожее на гонг. Что бы это могло значить..."

    label zone1_interaction:    
    
        menu:
            "Залезть на стол" if not on_table:
                $ on_table = True
                "Вы забрались на металлический стол."
            "Слезть со стола" if on_table:
                $ on_table = False
                "Вы слезли со стола."
            "Осмотреть динамик":
                "Ничего необычного, динамик как динамик."
            "Осмотреть пол":
                "Пол покрыт странными металлическими пластинами. Кажется, они проводят ток."
            "Просто подождать":
                "Ничего не произошло."
    
        $ rule = check_rules(current_zone)
        if rule:
            $ death_rule = rule
            jump death
        if timer_triggered:
            "Динамик издал короткий писк, после чего из него донеслось: 'Испытание пройдено. Дверь открыта. Проходите дальше'"
            "После этих слов дверь в конце комнаты открылась и вы поспешили в неё"
            $ current_zone = "zone2"
            jump zone_controller
        
        jump zone1_interaction

label death:
    if not is_rule_known(death_rule):
        $ rule_database.append(death_rule)
        "Вас настигает смерть. Нарушено новое правило: [death_rule.description] (Код: [death_rule.code])"
    else:
        "Вас настигает смерть. Нарушено известное правило: [death_rule.description]"

    if first_death:
        $ first_death = False
        "Что... что происходит? Я будто попал в ловушку абсурда..."
        "Нарушение правил приводит к смерти, но кажется сама смерть здесь - иллюзия..."

    show screen rule_database
    pause
    hide screen rule_database
    
    # Сброс состояния для текущей зоны
    if current_zone == "zone0":
        $ clicked_red = False
    elif current_zone == "zone1":
        $ on_table = False
        $ timer_triggered = False
        $ timer_active = False
    elif current_zone == "zone2":
        $ asked_about_time = False
        $ asked_about_village = False
        $ examined_body = False
        $ saw_footprints = False
        $ failed_solve = False
  
    jump zone_controller

screen zone0_objects:
    textbutton "Осмотреть стену":
        action Jump("inspect_wall_zone0")

label inspect_wall_zone0:
    "На стене выгравирована надпись: 'Правила не обсуждаются'"
    $ rule = check_rules(current_zone)
    if rule:
        $ death_rule = rule
        jump death
    jump zone0


label zone2:
    scene bg_village_square

    "Вы попадаете в огромную зону, всё так же ограниченную стенами, но перед собой видите полноценную деревню. На небе ночь и почти полная луна, но явно искуственно сделанные"
    "На деревенской площади у колодца собралась группа жителей. В центре - тело мужчины с пустым ведром."
    "Все они двигаются странно синхронно, как марионетки."
    "Вы подошли к ним и спросили что случилось."

    show villager1 at left
    show villager2 at right

    villager1 "Мы вместе набирали воду вчера в полдень. Тогда всё было нормально."
    villager2 "А вечером Марья видела, как он шёл к колодцу с пустым ведром..."

    label village_dialogue:
        menu:
            "Спросить про вечер" if not asked_about_time:
                villager1 "Да, около полуночи. Луна была полная, ярко светила."
                villager2 "Марья говорит, он как будто спешил, хотя ночью у колодца делать нечего."
                $ asked_about_time = True
                jump village_dialogue

            "Осмотреть тело" if not examined_body:
                "На теле нет никаких повреждений, только легкий запах озона."
                $ examined_body = True
                jump village_dialogue
            
            "Спросить про деревню" if not asked_about_village:
                villager1 "Это наша деревня. Живём здесь уже много лет."
                villager2 "Всё как везде - колодец, дома, поля..."
                $ asked_about_village = True
                jump village_dialogue

            "Спросить про эксперимент" if not asked_about_experiment:
                villager1 "Эксперимент? Нет, у нас только ярмарка бывает по осени."
                villager2 "Может, вы про новый способ воду доставать? Тоже вроде эксперимент."
                $ asked_about_experiment = True
                if not understood_npc_nature and asked_about_experiment and asked_about_lab:
                    $ understood_npc_nature = True
                    "Вы понимаете, что эти 'люди' - всего лишь часть системы. Нужно сосредоточиться на изучении правил этого мира."
                jump village_dialogue
            
            "Упомянуть лабораторные стены" if not asked_about_lab:
                $ asked_about_lab = True
                villager1 "Лаборатория? У нас только кузница да амбар."
                villager2 "Стены... да, стены у колодца новые, в прошлом месяце поставили."
                if not understood_npc_nature and asked_about_experiment and asked_about_lab:
                    $ understood_npc_nature = True
                    "Вы понимаете, что эти 'люди' - всего лишь часть системы. Нужно сосредоточиться на изучении правил этого мира."
                jump village_dialogue
            "Отправиться к колодцу":
                jump well

    label well:
        scene bg_village_well with dissolve
        "Вы подходите к колодцу. Вода кажется чистой, но металический ободок странно вибрирует. Издаётся глухой гул."
        label well_investigation:
            menu:
                "Набрать воду":
                    "Вы опускаете ведро в темную воду..."
                    $ fetched_water_at_night = True
                    "По телу проходит сильный заряд электричества. Последняя мысль: 'вода в колодце находится пол электричеством'"
                    $ rule = check_rules(current_zone)
                    if rule:
                        $ death_rule = rule
                        jump death

                "Осмотреть механизм" if not saw_footprints:
                    "На земле странные круговые отметины, будто от разрядов."
                    $ saw_footprints = True
                    jump well_investigation
                
                "Мне всё понятно, отправиться к старосте":
                    jump mayor_house
    
    label mayor_house:
        scene bg_village_house
        show mayor

        "Вы входите в просторный дом, староста сидит за столом, смотрит какие-то бумаги. Вы кашлянули и он вас заметил"
        mayor "Что вы хотели сказать? Вы узнали что-то по поводу смерти?"

        "Вы рассказываете старосте всё что знаете"
        if fetched_water_at_night and not asked_about_time:
            mayor "Колодцем пользоваться нельзя. А вода скоро закончится. Что же делать?.."
            $ failed_solve = True
            $ rule = check_rules(current_zone)
            if rule:
                $ death_rule = rule
                jump death
        
        if not fetched_water_at_night:
            mayor "Это нам было известно и без вас."
            $ failed_solve = True
            $ rule = check_rules(current_zone)
            if rule:
                $ death_rule = rule
                jump death
        
        if fetched_water_at_night and asked_about_time:
            mayor "Стало быть, ночью колодцем нельзя пользоваться. Да, о подобном меня предупреждали, но я не придал этому значения. Я оповещу всех в деревне. Благодарю за помощь"
            hide mayor
            "Староста встал и быстро покинул дом, оставив вас одного в нём. Позади того места где он сидел вы заметили дверь со знаком как в прошлых зонах. Судя по всему этот знак - выход в следующую зону"
            "Дверь открылась и вы направились по лестнице куда-то вниз..."
            "На этом история пока что заканчивается"



screen rule_database:
    frame:
        xalign 0.5
        yalign 0.1
        vbox:
            text "Собранные правила:"
            for rule in rule_database:
                text "- [rule.description] ([rule.code])"