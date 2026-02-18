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
    type: str
    modifier: str
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


def _parse_date(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        ts = value / 1000 if value > 1e12 else value
        return datetime.utcfromtimestamp(ts)
    if isinstance(value, str):
        try:
            ts = int(value)
            ts = ts / 1000 if ts > 1e12 else ts
            return datetime.utcfromtimestamp(ts)
        except ValueError:
            return datetime.fromisoformat(value)
    if isinstance(value, dict):
        if "$numberLong" in value:
            return _parse_date(value["$numberLong"])
        if "$date" in value:
            return _parse_date(value["$date"])
    return None


class WorldState(BaseModel):
    world_seed: str
    api_version: int
    mobile_version: str
    build_label: str
    current_event: Optional[Event] = None
    current_alerts: List[Alert]
    sortie: Sortie
    syndicate_missions: List[SyndicateMission]
    void_fissures: List[VoidFissure]
    global_boosts: List[BoostType]
    void_traders: List[VoidTrader]
    prime_resurgence: Optional[PrimeResurgence] = None
    prime_token_availability: bool
    daily_deals: List[DailyDeal]
    pvp_alternative_modes: List[ConclaveChallenge]
    invasion_construction_statuses: Tuple[float, float]
    feature_dojos: List[FeaturedDojo]
    season_info: SeasonInfo


def _parse_prime_resurgence(raw) -> Optional[PrimeResurgence]:
    if not raw:
        return None
    pr = raw[0] if isinstance(raw, list) else raw
    return PrimeResurgence(
        activation=_parse_date(pr.get("Activation")),
        expiry=_parse_date(pr.get("Expiry")),
        initial_start_date=_parse_date(pr.get("InitialStartDate")),
        node=pr.get("Node", ""),
        manifest=[
            PrimeResurgenceItem(
                item_type=pi.get("ItemType", ""),
                price=pi.get("PrimePrice", 0),
            )
            for pi in pr.get("Manifest", [])
        ],
        evergreen_manifest=[
            PrimeResurgenceItem(
                item_type=pi.get("ItemType", ""),
                price=pi.get("PrimePrice", 0),
            )
            for pi in pr.get("EvergreenManifest", [])
        ],
        schedule_info=[
            PrimeResurgenceScheduleInfo(
                expiry=_parse_date(info.get("Expiry")),
                featured_item=info.get("FeaturedItem", ""),
                preview_hidden_until=_parse_date(info.get("PreviewHiddenUntil")),
            )
            for info in pr.get("ScheduleInfo", [])
        ],
    )


def parse_worldstate(ws: dict) -> WorldState:
    events = ws.get("Events") or []
    event = events[0] if events else ws.get("Event") or {}
    current_event = Event(
        messages=[Message(**message) for message in event.get("Messages", [])],
        is_mobile_only=event.get("MobileOnly", False),
        priority=event.get("Priority", False),
        prop=event.get("Prop", ""),
        community=event.get("Community", False),
        icon=event.get("Icon", ""),
        image_url=event.get("ImageUrl", ""),
        date=_parse_date(event.get("Date")),
        start_date=_parse_date(event.get("EventStartDate")),
        end_date=_parse_date(event.get("EventEndDate")),
        live_url=event.get("EventLiveUrl", ""),
        do_hide_end_date_modifier=event.get("HideEndDateModifier", True),
        links=[Link(**link) for link in event.get("Links", [])],
    ) if event else None

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
                activation=_parse_date(alert.get("Activation")),
                expiry=_parse_date(alert.get("Expiry")),
                mission_info=mission_info,
                tag=alert.get("Tag", ""),
                force_unlock=alert.get("ForceUnlock", False),
            )
        )

    sorties_raw = ws.get("Sorties", [])
    sortie_data = sorties_raw[0] if isinstance(sorties_raw, list) and sorties_raw else (sorties_raw if isinstance(sorties_raw, dict) else {})
    sortie_missions = []
    for m in sortie_data.get("Variants", []):
        sortie_missions.append(
            SortieMission(
                type=m.get("missionType", ""),
                modifier=m.get("modifierType", ""),
                mission=m.get("node", ""),
                tileset=m.get("tileset", ""),
            )
        )
    sortie = Sortie(
        activation=_parse_date(sortie_data.get("Activation")),
        expiry=_parse_date(sortie_data.get("Expiry")),
        boss=sortie_data.get("Boss", ""),
        reward=sortie_data.get("Reward", ""),
        extra_drops=sortie_data.get("ExtraDrops", []),
        seed=sortie_data.get("Seed", 0),
        missions=sortie_missions,
    )

    worldstate = WorldState(
        world_seed=ws.get("WorldSeed", ""),
        api_version=ws.get("Version", 0),
        mobile_version=ws.get("MobileVersion", ""),
        build_label=ws.get("BuildLabel", ""),
        current_event=current_event,
        current_alerts=current_alerts,
        sortie=sortie,
        syndicate_missions=[
            SyndicateMission(
                activation=_parse_date(sm.get("Activation")),
                expiry=_parse_date(sm.get("Expiry")),
                syndicate_tag=sm.get("Tag", ""),
                nodes=sm.get("Nodes", []),
                open_world_missions=[
                    OpenWorldMission(
                        type=job.get("jobType", ""),
                        mastery_required=job.get("masteryReq", 0),
                        max_enemy_level=job.get("maxEnemyLevel", 0),
                        min_enemy_level=job.get("minEnemyLevel", 0),
                        rewards_table=job.get("rewards", ""),
                        xp_amounts=job.get("xpAmounts", []),
                    )
                    for job in sm.get("Jobs", [])
                ]
                if "Jobs" in sm
                else None,
            )
            for sm in ws.get("SyndicateMissions", [])
        ],
        void_fissures=[
            VoidFissure(
                activation=_parse_date(fissure.get("Activation")),
                expiry=_parse_date(fissure.get("Expiry")),
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
                activation=_parse_date(trader.get("Activation")),
                expiry=_parse_date(trader.get("Expiry")),
                node=trader.get("Node", ""),
                character=trader.get("Character", ""),
            )
            for trader in ws.get("VoidTraders", [])
        ],
        prime_resurgence=_parse_prime_resurgence(ws.get("PrimeResurgence")),
        prime_token_availability=ws.get("PrimeTokenAvailability", False),
        daily_deals=[
            DailyDeal(
                activation=_parse_date(deal.get("Activation")),
                expiry=_parse_date(deal.get("Expiry")),
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
                activation=_parse_date(challenge.get("startDate")),
                expiry=_parse_date(challenge.get("endDate")),
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
            activation=_parse_date(ws.get("SeasonInfo", {}).get("Activation")),
            expiry=_parse_date(ws.get("SeasonInfo", {}).get("Expiry")),
            affiliation_tag=ws.get("SeasonInfo", {}).get("AffiliationTag", ""),
            parameters=ws.get("SeasonInfo", {}).get("Params", ""),
            phase=ws.get("SeasonInfo", {}).get("Phase", 0),
            season=ws.get("SeasonInfo", {}).get("Season", 0),
            active_challenges=[
                MissionChallenge(
                    activation=_parse_date(challenge.get("Activation")),
                    challenge=challenge.get("Challenge", ""),
                    daily=challenge.get("Daily", False),
                    expiry=_parse_date(challenge.get("Expiry")),
                )
                for challenge in ws.get("SeasonInfo", {}).get("ActiveChallenges", [])
            ],
        ),
    )

    return worldstate
