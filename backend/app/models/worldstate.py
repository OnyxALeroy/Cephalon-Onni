from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class Message(BaseModel):
    LanguageCode: str
    Message: str


class Link(BaseModel):
    LanguageCode: str
    Link: str


# -------------------------------------------------------------------------------------------------


def get_enum_instance(enum_class, value):
    try:
        return enum_class(value)
    except ValueError:
        return None


class Plateform(str, Enum):
    PLATFORM_CROSS_PLATFORM = "Cross Platform"
    PLATFORM_SWITCH = "Switch"
    PLATFORM_PC = "PC"
    PLATFORM_XBOX = "Xbox"
    PLATFORM_PLAYSTATION = "PlayStation"


class MissionType(str, Enum):
    rescue = "Rescue"
    assault = "Assault"
    assassination = "Assassination"
    mobile_defense = "Mobile Defense"
    defense = "Defense"
    survival = "Survival"
    disruption = "Disruption"
    exterminate = "Exterminate"
    interception = "Interception"
    hijack = "Hijack"
    sabotage = "Sabotage"
    spy = "Spy"
    defection = "Defection"


class SortieModifier(str, Enum):
    fire = "Fire"
    radiation_hazard = "Radiation Hazard"
    energy_reduction = "Energy Reduction"
    augmented_enemy_armor = "Augmented Enemy Armor"
    augmented_enemy_shields = "Augmented Enemy Shields"
    enemy_elemental_enhancement = "Enemy Elemental Enhancement"
    enemy_physical_enhancement = "Enemy Physical Enhancement"
    enemy_speed_boost = "Enemy Speed Boost"
    eximus_stronghold = "Eximus Stronghold"
    weapon_type_only = "Weapon Type Only"
    electromagnetic_anomalies = "Electromagnetic Anomalies"


class Syndicate(str, Enum):
    steel_meridian = "Steel Meridian"
    SteelMeridianSyndicate = "Steel Meridian"
    CephalonSudaSyndicate = "Cephalon Suda"
    PerrinSyndicate = "The Perrin Sequence"
    ArbitersSyndicate = "Arbiters of Hexis"
    RedVeilSyndicate = "Red Veil"
    NewLokaSyndicate = "New Loka"
    VoxSyndicate = "Vox Solaris"
    QuillsSyndicate = "The Quills"
    AssassinsSyndicate = "The Assassins"
    VentKidsSyndicate = "Ventkids"
    EventSyndicate = "Operational Supply"
    NecraloidSyndicate = "Necraloid"
    CetusSyndicate = "Ostron"
    SolarisSyndicate = "Solaris United"
    EntratiSyndicate = "Entrati"
    ZarimanSyndicate = "The Holdfasts"
    RadioLegionSyndicate = "Nightwave Series 1"
    RadioLegion2Syndicate = "Nightwave Series 2"
    RadioLegion3Syndicate = "Nightwave Series 3"
    RadioLegionIntermissionSyndicate = "Nightwave Intermission"
    RadioLegionIntermission2Syndicate = "Nightwave Intermission 2"
    RadioLegionIntermission3Syndicate = "Nightwave Intermission 3"
    RadioLegionIntermission4Syndicate = "Nightwave: Nora's Choice"
    RadioLegionIntermission5Syndicate = "Nightwave: Nora's Mix Volume 1"
    RadioLegionIntermission6Syndicate = "Nightwave: Nora's Mix Volume 2"
    RadioLegionIntermission7Syndicate = "Nightwave: Nora's Mix Volume 3"


class RelicEra(str, Enum):
    lith = "Lith"
    meso = "Meso"
    neo = "Neo"
    axi = "Axi"
    requiem = "Requiem"
    omnia = "Omnia"


def get_relic_era_from_tier(value: str) -> RelicEra:
    if value == "VoidT1":
        return RelicEra.lith
    elif value == "VoidT2":
        return RelicEra.meso
    elif value == "VoidT3":
        return RelicEra.neo
    elif value == "VoidT4":
        return RelicEra.axi
    elif value == "VoidT5":
        return RelicEra.requiem
    elif value == "VoidT6":
        return RelicEra.omnia
    else:
        raise ValueError(f"Invalid RelicEra tier value: {value}")


class BoostType(str, Enum):
    affinity = "Affinity"
    credits = "Credits"
    resources = "Resources"


class Faction(str, Enum):
    grineer = "Grineer"
    corpus = "Corpus"
    infested = "Infested"


class PVPMode(str, Enum):
    all = "ALL"
    capture_the_flag = "CAPTURETHEFLAG"
    deathmatch = "DEATHMATCH"
    team_deathmatch = "TEAMDEATHMATCH"
    speed_ball = "SPEEDBALL"
    none = "NONE"


# -------------------------------------------------------------------------------------------------


class MissionRewardItem(BaseModel):
    item_type: str
    item_count: int


class MissionReward(BaseModel):
    credits: int
    counted_items: List[MissionRewardItem]


class MissionChallenge(BaseModel):
    activation: datetime
    challenge: str
    daily: bool
    expiry: datetime


class OpenWorldMission(BaseModel):
    type: str
    mastery_required: int
    max_enemy_level: int
    min_enemy_level: int
    rewards_table: str
    xp_amounts: List[int]


# -------------------------------------------------------------------------------------------------


class MissionInfo(BaseModel):
    location: str
    mission_type: str
    faction: str
    difficulty: int
    mission_reward: dict
    level_override: str
    enemy_spec: str
    min_enemy_level: int
    max_enemy_level: int
    desc_text: str
    max_wave_num: int


class Event(BaseModel):
    messages: List[Message]
    is_mobile_only: bool
    priority: bool
    prop: str
    community: bool
    icon: str
    image_url: str
    date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    live_url: str
    do_hide_end_date_modifier: bool
    links: List[Link]


class Alert(BaseModel):
    activation: datetime
    expiry: datetime
    mission_info: MissionInfo
    tag: str
    force_unlock: bool


class SyndicateMission(BaseModel):
    activation: datetime
    expiry: datetime
    syndicate_tag: str
    nodes: list
    open_world_missions: Optional[List[OpenWorldMission]] = None


class VoidFissure(BaseModel):
    activation: datetime
    expiry: datetime
    mission_type: str
    node: str
    region: int
    seed: int
    era: RelicEra


# -------------------------------------------------------------------------------------------------


class SortieMission(BaseModel):
    type: MissionType
    modifier: SortieModifier
    mission: str
    tileset: str


class Sortie(BaseModel):
    activation: datetime
    expiry: datetime
    boss: str
    reward: str
    extra_drops: list
    seed: int
    missions: List[SortieMission]


class Invasion(BaseModel):
    mission: str
    loc_tag: str
    activation: datetime
    attacker_faction: Faction
    defender_faction: Faction
    attacker_reward: List[MissionRewardItem]
    defender_reward: List[MissionRewardItem]


class VoidTrader(BaseModel):
    activation: datetime
    expiry: datetime
    node: str
    character: str


class PrimeResurgenceItem(BaseModel):
    item_type: str
    price: int


class PrimeResurgenceScheduleInfo(BaseModel):
    expiry: datetime
    featured_item: str
    preview_hidden_until: datetime


class PrimeResurgence(BaseModel):
    activation: datetime
    expiry: datetime
    node: str
    initial_start_date: datetime
    manifest: List[PrimeResurgenceItem]
    evergreen_manifest: List[PrimeResurgenceItem]
    schedule_info: List[PrimeResurgenceScheduleInfo]


class VoidStorm(BaseModel):
    activation: datetime
    expiry: datetime
    era: RelicEra
    mission: str


class DailyDeal(BaseModel):
    activation: datetime
    expiry: datetime
    original_price: int
    sale_price: int
    item: str
    sold_amount: int
    total_amount: int


class ConclaveChallenge(BaseModel):
    activation: datetime
    expiry: datetime
    category: str
    pvp_mode: PVPMode
    challenge_type_id: str
    challenge_sub_challenges: List[str]


class FeaturedDojo(BaseModel):
    alliance_id: str
    has_emblem: bool
    platforms: Dict[str, bool]
    icon_override: int
    name: str
    tier: int


class SeasonInfo(BaseModel):
    activation: datetime
    expiry: datetime
    affiliation_tag: str
    parameters: str
    phase: int
    season: int
    active_challenges: List[MissionChallenge]


# -------------------------------------------------------------------------------------------------


class WorldState(BaseModel):
    world_seed: str
    api_version: str
    mobile_version: str
    date: datetime
    current_event: Event
    current_alerts: List[Alert]
    sortie: Sortie
    syndicate_missions: List[SyndicateMission]
    void_fissures: List[VoidFissure]
    global_boosts: List[BoostType]
    void_traders: List[VoidTrader]
    prime_resurgence: PrimeResurgence
    prime_token_availability: bool
    daily_deals: List[DailyDeal]
    pvp_alternative_modes: List[ConclaveChallenge]
    invasion_construction_statuses: Tuple[float, float]
    feature_dojos: List[FeaturedDojo]
    season_info: SeasonInfo


def get_worldstate(url: str) -> WorldState:
    import requests

    response = requests.get(url)
    response.raise_for_status()
    ws = response.json()

    # Events
    event = ws.get("Event", {})
    current_event = Event(
        messages=[Message(**message) for message in event.get("Messages", [])],
        is_mobile_only=event.get("MobileOnly", False),
        priority=event.get("Priority", False),
        prop=event.get("Prop", ""),
        community=event.get("Community", False),
        icon=event.get("Icon", ""),
        image_url=event.get("ImageUrl", ""),
        date=event.get("Date", None),
        start_date=event.get("EventStartDate", None),
        end_date=event.get("EventEndDate", None),
        live_url=event.get("EventLiveUrl", ""),
        do_hide_end_date_modifier=event.get("HideEndDateModifier", True),
        links=[Link(**link) for link in event.get("Links", [])],
    )

    # Alerts
    current_alerts = []
    for alert in ws.get("Alerts", []):
        mi = alert.get("MissionInfo", {})
        mission_info = MissionInfo(
            location=mi.get("location", ""),
            mission_type=mi.get("missionType", ""),
            faction=mi.get("faction", ""),
            difficulty=mi.get("difficulty", 0),
            mission_reward=mi.get("missionReward", {}),
            level_override=mi.get("levelOverride", ""),
            enemy_spec=mi.get("enemySpec", ""),
            min_enemy_level=mi.get("minEnemyLevel", 0),
            max_enemy_level=mi.get("maxEnemyLevel", 0),
            desc_text=mi.get("descText", ""),
            max_wave_num=mi.get("maxWaveNum", 0),
        )
        current_alerts.append(
            Alert(
                activation=alert.get("Activation", {}).get("$date", None),
                expiry=alert.get("Expiry", {}).get("$date", None),
                mission_info=mission_info,
                tag=alert.get("Tag", ""),
                force_unlock=alert.get("ForceUnlock", False),
            )
        )

    # Sortie
    sortie_missions = []
    for m in ws.get("Sorties", {}).get("Variants", []):
        sortie_missions.append(
            SortieMission(
                type=get_enum_instance(MissionType, m.get("missionType", "")),
                modifier=get_enum_instance(SortieModifier, m.get("modifierType", "")),
                mission=m.get("node", ""),
                tileset=m.get("tileset", ""),
            )
        )
    sortie = Sortie(
        activation=ws.get("Sorties", {}).get("Activation", {}).get("$date", {}),
        expiry=ws.get("Sorties", {}).get("Expiry", {}).get("$date", {}),
        boss=ws.get("Sorties", {}).get("Boss", ""),
        reward=ws.get("Sorties", {}).get("Reward", ""),
        extra_drops=ws.get("Sorties", {}).get("ExtraDrops", []),
        seed=ws.get("Sorties", {}).get("Seed", 0),
        missions=sortie_missions,
    )

    worldstate = WorldState(
        world_seed=ws.get("WorldSeed", ""),
        api_version=ws.get("Version", ""),
        mobile_version=ws.get("MobileVersion", ""),
        date=ws.get("BuildLabel", datetime.now()),
        current_event=current_event,
        current_alerts=current_alerts,
        sortie=sortie,
        syndicate_missions=[
            SyndicateMission(
                activation=syndicate_mission.get("Activation", {}).get(
                    "$date", datetime.now()
                ),
                expiry=syndicate_mission.get("Expiry", {}).get("$date", datetime.now()),
                syndicate_tag=syndicate_mission.get("Tag", ""),
                nodes=syndicate_mission.get("Nodes", []),
                open_world_missions=[
                    OpenWorldMission(
                        type=job.get("jobType", ""),
                        mastery_required=job.get("masteryReq", 0),
                        max_enemy_level=job.get("maxEnemyLevel", 0),
                        min_enemy_level=job.get("minEnemyLevel", 0),
                        rewards_table=job.get("rewards", ""),
                        xp_amounts=job.get("xpAmounts", []),
                    )
                    for job in syndicate_mission.get("Jobs", [])
                ]
                if "Jobs" in syndicate_mission.keys()
                else None,
            )
            for syndicate_mission in ws.get("SyndicateMissions", [])
        ],
        void_fissures=[
            VoidFissure(
                activation=fissure.get("Activation", {}).get("$date", datetime.now()),
                expiry=fissure.get("Expiry", {}).get("$date", datetime.now()),
                mission_type=fissure.get("MissionType", ""),
                era=get_relic_era_from_tier(fissure.get("Modifier", "")),
                seed=fissure.get("Seed", 0),
                region=fissure.get("Region", 0),
                node=fissure.get("Node", ""),
            )
            for fissure in ws.get("ActiveMissions", [])
        ],
        global_boosts=[
            get_enum_instance(BoostType, b) for b in ws.get("GlobalUpgrades", [])
        ],
        void_traders=[
            VoidTrader(
                activation=trader.get("Activation", {}).get("$date", datetime.now()),
                expiry=trader.get("Expiry", {}).get("$date", datetime.now()),
                node=trader.get("Node", ""),
                character=trader.get("Character", ""),
            )
            for trader in ws.get("VoidTraders", [])
        ],
        prime_resurgence=PrimeResurgence(
            activation=ws.get("PrimeResurgence", [])[0]
            .get("Activation", {})
            .get("$date", datetime.now()),
            expiry=ws.get("PrimeResurgence", [])[0]
            .get("Expiry", {})
            .get("$date", datetime.now()),
            initial_start_date=ws.get("PrimeResurgence", [])[0]
            .get("InitialStartDate", {})
            .get("$date", datetime.now()),
            node=ws.get("PrimeResurgence", [])[0].get("Node", ""),
            manifest=[
                PrimeResurgenceItem(
                    item_type=prime_item.get("ItemType", ""),
                    price=prime_item.get("PrimePrice", 0),
                )
                for prime_item in ws.get("PrimeResurgence", [])[0].get("Manifest", [])
            ],
            evergreen_manifest=[
                PrimeResurgenceItem(
                    item_type=prime_item.get("ItemType", ""),
                    price=prime_item.get("PrimePrice", 0),
                )
                for prime_item in ws.get("PrimeResurgence", [])[0].get(
                    "EvergreenManifest", []
                )
            ],
            schedule_info=[
                PrimeResurgenceScheduleInfo(
                    expiry=info.get("Expiry", {}).get("$date", datetime.now()),
                    featured_item=info.get("FeaturedItem", ""),
                    preview_hidden_until=info.get("PreviewHiddenUntil", {}).get(
                        "$date", datetime.now()
                    ),
                )
                for info in ws.get("PrimeResurgence", [])[0].get("ScheduleInfo", [])
            ],
        ),
        prime_token_availability=ws.get("PrimeTokenAvailability", False),
        daily_deals=[
            DailyDeal(
                activation=deal.get("Activation", {})
                .get("$date", {})
                .get("$numberLong", datetime.now()),
                expiry=deal.get("Activation", {})
                .get("$date", {})
                .get("$numberLong", datetime.now()),
                original_price=deal.get("OriginalPrice", 0),
                sale_price=deal.get("SalePrice", 0),
                item=deal.get("StoreItem", ""),
                sold_amount=deal.get("AmountSold", 0),
                total_amount=deal.get("AmountTotal", 0),
            )
            for deal in ws.get("DailyDeals", [])
        ],
        pvp_alternative_modes=[
            ConclaveChallenge(
                activation=challenge.get("startDate", {})
                .get("$date", {})
                .get("$numberLong", datetime.now()),
                expiry=challenge.get("endDate", {})
                .get("$date", {})
                .get("$numberLong", datetime.now()),
                category=challenge.get("Category", ""),
                pvp_mode=get_enum_instance(
                    PVPMode,
                    challenge.get("PVPMode", "").replace("PVPMODE_", "").upper(),
                ),
                challenge_type_id=challenge.get("challengeTypeRefID", ""),
                challenge_sub_challenges=[
                    sub_challenge.get("$oid", "")
                    for sub_challenge in challenge.get("subChallenges", {})
                ],
            )
            for challenge in ws.get("PVPChallengeInstances", [])
        ],
        invasion_construction_statuses=(
            ws.get("ProjectPct", [0.0, 0.0])[0],
            ws.get("ProjectPct", [0.0, 0.0])[1],
        ),
        feature_dojos=[
            FeaturedDojo(
                alliance_id=dojo.get("AllianceId", {}).get("$oid", ""),
                has_emblem=dojo.get("Emblem", False),
                platforms=dojo.get("HiddenPlatforms", {}),
                icon_override=dojo.get("IconOverride", 0),
                name=dojo.get("Name", ""),
                tier=dojo.get("Tier", 0),
            )
            for dojo in ws.get("FeaturedGuilds", [])
        ],
        season_info=SeasonInfo(
            activation=ws.get("SeasonInfo", {})
            .get("Activation", {})
            .get("$date", {})
            .get("$numberLong", 0),
            expiry=ws.get("SeasonInfo", {})
            .get("Expiry", {})
            .get("$date", {})
            .get("$numberLong", 0),
            affiliation_tag=ws.get("SeasonInfo", {}).get("AffiliationTag", ""),
            parameters=ws.get("SeasonInfo", {}).get("Params", ""),
            phase=ws.get("SeasonInfo", {}).get("Phase", 0),
            season=ws.get("SeasonInfo", {}).get("Season", 0),
            active_challenges=[
                MissionChallenge(
                    activation=challenge.get("Activation", {})
                    .get("$date", {})
                    .get("$numberLong", 0),
                    challenge=challenge.get("Challenge", ""),
                    daily=challenge.get("Daily", False),
                    expiry=challenge.get("Expiry", {})
                    .get("$date", {})
                    .get("$numberLong", 0),
                )
                for challenge in ws.get("ActiveChallenges", [])
            ],
        ),
    )

    return worldstate
