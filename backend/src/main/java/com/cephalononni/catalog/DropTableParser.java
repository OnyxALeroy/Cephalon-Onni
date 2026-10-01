package com.cephalononni.catalog;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Parses the official drop-tables page (one big HTML document: an h3 per section, followed by
 * tables of header rows and item/chance rows) into one {@link DropRow} per (item, source,
 * rotation).
 *
 * Port of the legacy backend's parse_loot_tables_sync, with its data-loss bugs fixed: it keyed
 * each section's rows by item name only (an item dropping in 40 missions kept just the last
 * one), leaked the previous mission's rotation into missions without rotations, and ran the
 * inverted "Drops by Mod / by Item" tables through the "by Source" handler (producing items
 * named "15.00%"). Those inverted tables duplicate the "by Source" ones, so they're skipped.
 * It also ignored the "Relics" section entirely (each relic's reward chances per refinement);
 * those are now kept as source = relic name, rotation = refinement.
 */
public final class DropTableParser {

    public static final String MISSION = "mission";
    public static final String KEY = "key";
    public static final String DYNAMIC_LOCATION = "dynamic_location";
    public static final String SORTIE = "sortie";
    public static final String BOUNTY = "bounty";
    public static final String GENERAL_DROP = "general_drop";
    public static final String RELIC = "relic";

    /** "Mercury/Apollodorus (Survival)", optionally "Event: ..." or with a trailing " Extra". */
    private static final Pattern MISSION_HEADER = Pattern.compile("^(?:Event: )?([^/]+)/(.+?) \\(([^)]+)\\).*$");
    /** "Axi A1 Relic (Intact)" -> relic name + refinement */
    private static final Pattern RELIC_HEADER = Pattern.compile("^(.+?) \\((Intact|Exceptional|Flawless|Radiant)\\)$");
    /** "Rare (7.69%)" -> 7.69 */
    private static final Pattern CHANCE = Pattern.compile("\\(([\\d.]+)%?\\)");
    /** "Mod Drop Chance: 100.00%" -> 100.00% */
    private static final Pattern SOURCE_CHANCE = Pattern.compile("[\\d.]+%");

    private DropTableParser() {}

    /** A mission row's parsed "System/Node (Type)" header, used to fill missions.drops. */
    public record MissionRef(String systemName, String nodeName, String missionType) {
    }

    public record DropRow(String name, String sourceType, String source, double chance, String rotation,
                          MissionRef mission) {
    }

    public static List<DropRow> parse(String html) {
        Document document = Jsoup.parse(html);
        Map<String, List<List<String>>> sections = new LinkedHashMap<>();
        String currentTitle = null;
        for (Element element : document.select("h3, table")) {
            if (element.normalName().equals("h3")) {
                currentTitle = element.text().trim();
                continue;
            }
            if (currentTitle == null) {
                continue;
            }
            List<List<String>> rows = sections.computeIfAbsent(currentTitle, t -> new ArrayList<>());
            for (Element tr : element.select("tr")) {
                List<String> cells = tr.select("th, td").stream().map(cell -> cell.text().trim()).toList();
                if (cells.stream().allMatch(String::isEmpty)) {
                    continue;
                }
                rows.add(cells);
            }
        }

        Map<String, DropRow> rows = new LinkedHashMap<>();
        sections.forEach((title, sectionRows) -> parseSection(title, sectionRows, rows));
        return List.copyOf(rows.values());
    }

    private static void parseSection(String title, List<List<String>> rows, Map<String, DropRow> out) {
        if (title.equals("Missions:")) {
            parseMissions(rows, out);
        } else if (title.equals("Relics:")) {
            parseRelics(rows, out);
        } else if (title.equals("Keys:")) {
            parseHeaderedRotations(rows, KEY, out);
        } else if (title.equals("Dynamic Location Rewards:")) {
            parseHeaderedRotations(rows, DYNAMIC_LOCATION, out);
        } else if (title.equals("Sorties:")) {
            parseSorties(rows, out);
        } else if (title.endsWith("Bounty Rewards:")) {
            parseBounties(rows, title.substring(0, title.length() - 1), out);
        } else if (title.endsWith("Drops by Source:")) {
            parseDropsBySource(rows, out);
        }
    }

    private static void parseMissions(List<List<String>> rows, Map<String, DropRow> out) {
        String source = null;
        String rotation = null;
        MissionRef mission = null;
        for (List<String> row : rows) {
            if (row.size() == 1) {
                String header = row.get(0);
                if (isRotation(header)) {
                    rotation = header;
                } else {
                    source = header;
                    rotation = null;
                    Matcher matcher = MISSION_HEADER.matcher(header);
                    mission = matcher.matches()
                            ? new MissionRef(matcher.group(1).trim(), matcher.group(2).trim(), matcher.group(3).trim())
                            : null;
                }
            } else if (row.size() == 2 && source != null) {
                add(out, row.get(0), row.get(1), MISSION, source, rotation, mission);
            }
        }
    }

    /** Relics: an "Axi A1 Relic (Intact)" header per refinement, then [item, chance] rows. */
    private static void parseRelics(List<List<String>> rows, Map<String, DropRow> out) {
        String source = null;
        String refinement = null;
        for (List<String> row : rows) {
            if (row.size() == 1) {
                Matcher matcher = RELIC_HEADER.matcher(row.get(0));
                source = matcher.matches() ? matcher.group(1) : row.get(0);
                refinement = matcher.matches() ? matcher.group(2) : null;
            } else if (row.size() == 2 && source != null) {
                add(out, row.get(0), row.get(1), RELIC, source, refinement, null);
            }
        }
    }

    /** Keys and dynamic locations: a name header, optional "Rotation X" headers, item rows. */
    private static void parseHeaderedRotations(List<List<String>> rows, String sourceType, Map<String, DropRow> out) {
        String source = null;
        String rotation = null;
        for (List<String> rawRow : rows) {
            // Dynamic locations write rotation headers as <th>Rotation A</th><td></td>.
            List<String> row = rawRow.stream().filter(cell -> !cell.isEmpty()).toList();
            if (row.size() == 1) {
                if (isRotation(row.get(0))) {
                    rotation = row.get(0);
                } else {
                    source = row.get(0);
                    rotation = null;
                }
            } else if (row.size() == 2 && source != null) {
                add(out, row.get(0), row.get(1), sourceType, source, rotation, null);
            }
        }
    }

    private static void parseSorties(List<List<String>> rows, Map<String, DropRow> out) {
        for (List<String> row : rows) {
            if (row.size() == 2) {
                add(out, row.get(0), row.get(1), SORTIE, "Sortie", null, null);
            }
        }
    }

    /**
     * Bounties: a level header ("Level 5 - 15 Cetus Bounty"), rotation headers, stage headers
     * (["", "Stage 2, Stage 3 of 4, and Stage 3 of 5"]) and item rows (["", item, chance]).
     */
    private static void parseBounties(List<List<String>> rows, String bountyTitle, Map<String, DropRow> out) {
        String level = null;
        String rotation = null;
        String stages = null;
        for (List<String> row : rows) {
            if (row.size() == 1) {
                if (isRotation(row.get(0))) {
                    rotation = row.get(0);
                    stages = null;
                } else {
                    level = row.get(0);
                    rotation = null;
                    stages = null;
                }
            } else if (row.size() == 2) {
                stages = row.get(1);
            } else if (row.size() == 3 && level != null) {
                String label = rotation == null ? stages : stages == null ? rotation : rotation + " (" + stages + ")";
                add(out, row.get(1), row.get(2), BOUNTY, bountyTitle + " " + level, label, null);
            }
        }
    }

    /** "X Drops by Source": [enemy, "Mod Drop Chance: 3.00%"] headers, then ["", item, chance] rows. */
    private static void parseDropsBySource(List<List<String>> rows, Map<String, DropRow> out) {
        String source = null;
        for (List<String> row : rows) {
            if (row.size() == 1) {
                source = row.get(0);
            } else if (row.size() == 2) {
                Matcher matcher = SOURCE_CHANCE.matcher(row.get(1));
                source = matcher.find() ? row.get(0) + " (" + matcher.group() + ")" : row.get(0);
            } else if (row.size() == 3 && source != null && !row.get(0).equals("Source")) {
                add(out, row.get(1), row.get(2), GENERAL_DROP, source, null, null);
            }
        }
    }

    private static boolean isRotation(String cell) {
        return cell.startsWith("Rotation ");
    }

    private static void add(Map<String, DropRow> out, String item, String chanceCell, String sourceType,
                            String source, String rotation, MissionRef mission) {
        Matcher matcher = CHANCE.matcher(chanceCell);
        if (item.isEmpty() || !matcher.find()) {
            return;
        }
        double chance;
        try {
            chance = Double.parseDouble(matcher.group(1));
        } catch (NumberFormatException e) {
            return;
        }
        // Same key as the drop_sources unique constraint; the page repeats a few rows verbatim.
        String key = item + '\u0000' + source + '\u0000' + rotation;
        out.putIfAbsent(key, new DropRow(item, sourceType, source, chance, rotation, mission));
    }
}
