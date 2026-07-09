"""Exhibition document — Sulfuric Acid Contact Process theme.

Pure chemical technology focus. Uses fpdf2 (already in requirements.txt).

Usage:
    python -m sentinelgui.exhibition_doc

Output: sentinelgui_exhibition.pdf in the project root.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from fpdf import FPDF


def _s(text: str) -> str:
    text = str(text)
    text = text.replace("\u2014", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("\u00b0", " deg ")
    text = text.replace("\u0394", "dP")
    text = text.replace("\u00d7", "x")
    for i in range(10):
        text = text.replace(chr(0x2080 + i), str(i))
    return text.encode("ascii", errors="replace").decode("ascii")


def _heading(pdf, text: str, level: int = 1):
    sizes = {0: 18, 1: 14, 2: 12, 3: 10}
    pdf.set_font("Helvetica", "B", sizes.get(level, 12))
    pdf.set_text_color(20, 40, 100)
    pdf.cell(0, 8, _s(text), ln=True)
    pdf.set_text_color(0, 0, 0)


def _body(pdf, text: str):
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(text))
    pdf.ln(2)


def _body_bold(pdf, text: str):
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(0, 5, _s(text))
    pdf.ln(1)


def _footer(pdf):
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, _s(f"Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)


def generate(output_dir: str = ".") -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── Title page ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 40, 100)
    pdf.multi_cell(0, 10, _s("Real-Time Process Monitoring for the\nSulfuric Acid Contact Process"), align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, _s("A Chemical Technology Perspective on Fault Detection and Safety"), ln=True, align="C")
    pdf.ln(25)
    pdf.set_draw_color(20, 40, 100)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, _s("Usman Shamim"), ln=True, align="C")
    pdf.cell(0, 7, _s(datetime.datetime.now().strftime("%B %Y")), ln=True, align="C")
    pdf.ln(6)
    pdf.cell(0, 7, _s("Department of Chemical Technology Exhibition"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    # ── Members / Index ─────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "Project Members", 1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    col_m = [50, 100]
    pdf.cell(col_m[0], 7, _s("GR No"), border=1, align="C")
    pdf.cell(col_m[1], 7, _s("Name"), border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    members = [
        ["", "Muhammad Usman Bin Shamim"],
        ["", ""],
        ["", ""],
    ]
    for row in members:
        pdf.cell(col_m[0], 7, _s(row[0]), border=1)
        pdf.cell(col_m[1], 7, _s(row[1]), border=1)
        pdf.ln()
    pdf.ln(10)

    _heading(pdf, "Contents", 1)
    pdf.set_font("Helvetica", "", 10)
    toc = [
        "Abstract",
        "1. Introduction",
        "2. Thermodynamics and Kinetics of the Catalytic Oxidation",
        "3. Process Monitoring Parameters",
        "4. Fault Detection in the Contact Process",
        "5. Fault Analysis Summary",
        "6. Physical Demonstration Model",
        "7. Monitoring System Overview",
        "8. Conclusion",
        "References",
    ]
    for i, item in enumerate(toc, 1):
        pdf.cell(0, 6, _s(f"   {item}"), ln=True)
    _footer(pdf)

    # ── Abstract ────────────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "Abstract", 1)
    _body(pdf, (
        "Sulfuric acid (H2SO4) is the most-produced chemical by volume worldwide, with annual "
        "output exceeding 250 million metric tons. The dominant production route is the contact "
        "process, in which sulfur is burned to sulfur dioxide, catalytically oxidised to sulfur "
        "trioxide over vanadium pentoxide (V2O5), and absorbed in concentrated sulfuric acid. The "
        "catalytic oxidation step -- 2SO2 + O2 <-> 2SO3 -- is exothermic (dH = -99 kJ/mol) and "
        "reversible, requiring precise temperature control between 400 and 450 degC to maintain "
        "both high reaction rate and favourable equilibrium conversion."
    ))
    _body(pdf, (
        "This study examines the key process variables that must be monitored to ensure safe and "
        "efficient contact process operation: converter bed temperature, SO2 feed rate, and column "
        "pressure drop. Six distinct process fault scenarios are analysed from a chemical "
        "engineering standpoint -- catalyst bed plugging, air blower failure, acid pump cavitation, "
        "catalyst fouling, converter thermal runaway, and inter-bed cooling failure. Each fault is "
        "examined through its underlying chemical and physical mechanism, its sensor signature, and "
        "its economic and safety consequences. A real-time monitoring system (SentinelGUI) is "
        "presented that tracks these variables and diagnoses these faults automatically, "
        "demonstrating the practical application of chemical engineering fundamentals in industrial "
        "process safety."
    ))
    _footer(pdf)

    # ── 1. Introduction ─────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "1. Introduction", 1)

    _body(pdf, (
        "Sulfuric acid is a foundational chemical commodity. Its primary application is in the "
        "manufacture of phosphate fertilisers, which consume approximately 60% of global production. "
        "Other major uses include petroleum refining (alkylation catalysts), metal ore leaching "
        "(copper, uranium, zinc), industrial water treatment, and the production of dyes, "
        "pigments, detergents, and pharmaceuticals. The scale of production and the hazardous "
        "nature of the materials involved make process safety a paramount concern."
    ))

    _body_bold(pdf, "The Contact Process")
    _body(pdf, (
        "The contact process, commercialised in the late 19th century by the German chemical "
        "industry and refined continuously since, is today the universally adopted method for "
        "sulfuric acid manufacture. The process consists of three chemically distinct stages:"
    ))
    _body(pdf, (
        "Stage 1 -- Combustion of elemental sulfur:\n"
        "   S(s) + O2(g) -> SO2(g),   dH = -297 kJ/mol\n"
        "   Molten sulfur is sprayed into a combustion furnace with dried air at approximately "
        "1000 degC. The reaction is highly exothermic and self-sustaining once ignited. The "
        "resulting gas stream contains roughly 8-12% SO2 by volume, with the balance being N2, "
        "excess O2, and trace combustion products."
    ))
    _body(pdf, (
        "Stage 2 -- Catalytic oxidation of SO2 to SO3:\n"
        "   2SO2(g) + O2(g) <-> 2SO3(g),   dH = -99 kJ/mol\n"
        "   This is the critical step. The hot SO2-bearing gas is passed through a multi-bed "
        "catalytic converter containing promoted vanadium pentoxide (V2O5) on a silica support. "
        "The reaction proceeds at 400-450 degC. The equilibrium conversion of SO2 to SO3 is "
        "temperature-dependent: at 400 degC, approximately 99% of SO2 can be converted; at "
        "500 degC, the equilibrium conversion falls to approximately 93%. Inter-bed heat "
        "exchangers cool the partially reacted gas between catalyst beds to shift the equilibrium "
        "toward product formation."
    ))
    _body(pdf, (
        "Stage 3 -- Absorption of SO3:\n"
        "   SO3(g) + H2O(l) -> H2SO4(l),   dH = -130 kJ/mol\n"
        "   Sulfur trioxide cannot be absorbed directly in water, as the reaction forms a dense "
        "acid mist that is difficult to capture. Instead, SO3 is absorbed in circulating "
        "concentrated sulfuric acid (98-99% H2SO4), which reacts to form additional H2SO4. The "
        "product acid is continuously withdrawn and diluted with water to the desired "
        "concentration."
    ))

    _body_bold(pdf, "Why monitoring matters")
    _body(pdf, (
        "Each stage of the contact process operates under tightly constrained conditions. "
        "Deviation from the optimal temperature window in the catalytic converter reduces "
        "conversion efficiency and risks permanent catalyst damage. Feed rate imbalances can "
        "create explosive gas mixtures or cause environmental SO2 emissions. Cooling system "
        "failures can initiate thermal runaway. Real-time monitoring of key process variables "
        "is not merely an operational convenience but a fundamental safety requirement, analagous "
        "to the trip systems and interlocks found in all modern chemical process plants."
    ))
    _footer(pdf)

    # ── 2. Thermodynamics and Kinetics ──────────────────────────────────
    pdf.add_page()
    _heading(pdf, "2. Thermodynamics and Kinetics of the Catalytic Oxidation", 1)

    _body_bold(pdf, "Equilibrium considerations")
    _body(pdf, (
        "The oxidation of SO2 to SO3 is exothermic and reversible. Le Chatelier's principle "
        "predicts that lower temperatures favour the forward (product-forming) reaction, while "
        "higher temperatures favour the reverse decomposition. The equilibrium constant Kp for "
        "the reaction decreases with increasing temperature:"
    ))
    _body(pdf, (
        "   log10(Kp) = 5186/T - 0.611*log10(T) + 6.750\n\n"
        "where T is in Kelvin. At 400 degC (673 K), Kp is approximately 380; at 500 degC "
        "(773 K), Kp falls to approximately 40. This strong temperature dependence means that "
        "even modest overheating of a catalyst bed can significantly reduce the per-pass "
        "conversion."
    ))

    _body_bold(pdf, "Reaction kinetics")
    _body(pdf, (
        "The rate of SO2 oxidation over V2O5 catalyst follows the Arrhenius equation:"
    ))
    _body(pdf, (
        "   k = A * exp(-Ea / RT)\n\n"
        "where k is the rate constant, A is the pre-exponential factor (approximately "
        "3 x 10^5 s^-1 for commercial V2O5 catalysts), Ea is the activation energy "
        "(approximately 90-110 kJ/mol for the V2O5-catalysed reaction), R is the universal "
        "gas constant (8.314 J/mol.K), and T is absolute temperature."
    ))
    _body(pdf, (
        "Doubling the temperature from 400 degC to 500 degC increases the reaction rate by "
        "a factor of approximately 10, but simultaneously halves the equilibrium conversion. "
        "This tension between rate and conversion is resolved industrially by employing "
        "multiple catalyst beds with inter-bed cooling: the gas reacts partially in the first "
        "bed, is cooled, reacts further in the second bed, and so on. Modern converters "
        "typically have four or five beds, achieving overall conversions exceeding 99.5%."
    ))

    _body_bold(pdf, "Catalyst structure and deactivation")
    _body(pdf, (
        "The industrial catalyst consists of 6-8% V2O5 promoted with alkali metal sulfates "
        "(typically K2SO4 or Cs2SO4) and supported on diatomaceous silica. The active phase is "
        "a molten salt melt of alkali pyrosulfates (M2S2O7) that wets the support surface. "
        "SO2 and O2 dissolve in this melt and react to form SO3, which then desorbs into the "
        "gas phase."
    ))
    _body(pdf, (
        "Catalyst deactivation occurs through several mechanisms:\n\n"
        "- Sintering: At temperatures above 600 degC, the support structure collapses, "
        "reducing surface area and permanently destroying activity.\n\n"
        "- Poisoning: Arsenic compounds (As2O3) in the feed gas form stable, non-catalytic "
        "vanadium-arsenic complexes that block active sites.\n\n"
        "- Dust fouling: Fine particles from the sulfur combustion furnace physically block "
        "gas access to catalyst surfaces.\n\n"
        "- Thermal cycling: Repeated heating and cooling causes mechanical stress and "
        "catalyst attrition."
    ))
    _footer(pdf)

    # ── 3. Process Monitoring Parameters ────────────────────────────────
    pdf.add_page()
    _heading(pdf, "3. Process Monitoring Parameters", 1)

    _body(pdf, (
        "Three process variables provide a complete picture of converter health and are "
        "continuously monitored in real time:"
    ))

    _body_bold(pdf, "3.1 Converter Bed Temperature (degC)")
    _body(pdf, (
        "The temperature at the hottest point in each catalyst bed is the single most important "
        "indicator of converter condition. The normal operating range is 400-450 degC, with "
        "the peak temperature occurring just downstream of the bed inlet where the reaction "
        "rate is highest. A rising temperature trend indicates that the exothermic reaction is "
        "accelerating -- either because the inlet gas is too hot (inter-bed cooling failure) or "
        "because the catalyst activity has declined and the plant has increased the feed "
        "temperature to compensate (catalyst fouling). A falling temperature suggests feed "
        "interruption or excessively cold inlet gas. The temperature profile across the beds "
        "also reveals which bed is performing poorly: a bed with little temperature rise is "
        "contributing minimal conversion."
    ))

    _body_bold(pdf, "3.2 SO2 Feed Rate (L/min)")
    _body(pdf, (
        "The volumetric flow rate of SO2 entering the converter determines the production rate "
        "and must be maintained within strict limits relative to the available oxygen. The "
        "stoichiometric O2:SO2 ratio for the oxidation reaction is 0.5:1, but industrial "
        "practice uses excess oxygen (typically 1.5:1 to 2:1) to drive the equilibrium toward "
        "product. If the feed rate drops, production falls proportionally. If the feed rate "
        "rises above the design capacity of the converter, the residence time in the catalyst "
        "beds becomes insufficient for complete reaction, and unconverted SO2 is emitted to "
        "the absorption section and ultimately to the atmosphere."
    ))

    _body_bold(pdf, "3.3 Column Pressure Drop -- dP (bar)")
    _body(pdf, (
        "The pressure drop across the catalyst beds follows the Ergun equation for flow through "
        "packed beds:"
    ))
    _body(pdf, (
        "   dP/L = 150 * (1-e)^2/e^3 * mu*V / Dp^2 + 1.75 * (1-e)/e^3 * rho*V^2 / Dp\n\n"
        "where e is bed void fraction, mu is gas viscosity, V is superficial velocity, Dp is "
        "particle diameter, and rho is gas density. The first term dominates at low Reynolds "
        "numbers (viscous losses), and the second at high Reynolds numbers (inertial losses). "
        "In the contact process converter, operating in the transitional flow regime, both "
        "terms contribute."
    ))
    _body(pdf, (
        "A rising dP indicates that the bed void fraction is decreasing -- caused by dust "
        "accumulation, catalyst attrition fines, or the growth of sintered deposits. This is "
        "an early warning of bed plugging, which, if uncorrected, forces a costly shutdown for "
        "catalyst screening or replacement. A falling dP combined with falling flow rate "
        "indicates a blower or upstream feed failure."
    ))
    _footer(pdf)

    # ── 4. Fault Detection ──────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "4. Fault Detection in the Contact Process", 1)

    _body(pdf, (
        "Six distinct process fault scenarios can be identified from the sensor signatures. Each "
        "fault is described below in terms of its chemical engineering mechanism, the resulting "
        "sensor pattern, and the industrial consequence if left unaddressed."
    ))

    _body_bold(pdf, "Fault 1 -- Catalyst Bed Plugging")
    _body(pdf, (
        "Mechanism: Fine particulate matter from the sulfur combustion furnace (ash, unburned "
        "sulfur dust) or catalyst attrition debris accumulates in the interstitial spaces between "
        "catalyst pellets. The bed void fraction (e) decreases, causing the pressure drop to "
        "rise per the Ergun equation. At the same time, the resistance to flow reduces the "
        "volumetric throughput.\n\n"
        "Sensor signature: Column dP rises progressively while SO2 feed rate declines. The "
        "ratio dP/flow increases above normal.\n\n"
        "Consequence: Reduced production rate. If plugging continues, the bed may require "
        "screening (removing and sieving the catalyst) or full replacement -- a 7-14 day "
        "shutdown involving cooling, catalyst handling, and significant labour and material cost."
    ))

    _body_bold(pdf, "Fault 2 -- Air Blower Failure")
    _body(pdf, (
        "Mechanism: The main air blower or SO2 circulator trips or loses power. Without forced "
        "draught, the gas flow through the converter stops. The catalytic reaction ceases "
        "immediately because reactants cannot reach the catalyst surface -- the process is "
        "mass-transfer-limited, and without convective flow the diffusion path from the bulk "
        "gas to the catalyst melt is effectively infinite.\n\n"
        "Sensor signature: Feed rate collapses to near zero. Column pressure equalises to "
        "atmospheric (dP approaches zero). Temperatures across the beds fall as the exotherm "
        "extinguishes.\n\n"
        "Consequence: Complete production halt. Risk of SO2 backflow into air ducts and acid "
        "condensation in cold sections of the plant, causing corrosion. Blower restart "
        "procedures must account for potential explosive atmospheres if SO2 concentrations "
        "exceed safe limits."
    ))

    _body_bold(pdf, "Fault 3 -- Acid Pump Cavitation")
    _body(pdf, (
        "Mechanism: In the absorption tower circuit, centrifugal pumps circulate concentrated "
        "sulfuric acid over the packing. If the static pressure at the pump suction falls below "
        "the vapour pressure of the acid, vapour bubbles nucleate at the impeller eye. These "
        "bubbles collapse violently against the blade surfaces in the high-pressure region of "
        "the pump, generating localised shock waves that erode the impeller material -- a "
        "phenomenon known as cavitation. Net Positive Suction Head (NPSH) available drops below "
        "NPSH required.\n\n"
        "Sensor signature: Low, oscillating pressure in the acid circulation line with "
        "significantly higher variance than normal operation.\n\n"
        "Consequence: Progressive mechanical destruction of the pump impeller, pump failure, "
        "loss of acid circulation, SO3 breakthrough to the atmosphere, environmental emission "
        "violation, and potential plant shutdown."
    ))

    _body_bold(pdf, "Fault 4 -- Catalyst Fouling and Poisoning")
    _body(pdf, (
        "Mechanism: Impurities in the feed gas -- particularly arsenic trioxide (As2O3) from "
        "sulfur feedstocks, but also dust and volatilised support components -- gradually "
        "interact with the active vanadium species. Arsenic forms stable arsenate complexes "
        "with vanadium (e.g., V2O5.As2O3) that have no catalytic activity for SO2 oxidation. "
        "As active sites are blocked, the catalyst's effectiveness factor declines. Operators "
        "compensate by raising the inlet gas temperature to maintain conversion, but this "
        "accelerates the sintering rate of the remaining active surface.\n\n"
        "Sensor signature: Converter temperature rises slowly over days to weeks as the plant "
        "increases firing to compensate. Feed rate may drop mildly as bed restriction develops."
        " The temperature at which a given conversion is achieved shifts upward.\n\n"
        "Consequence: Reduced SO2-to-SO3 conversion efficiency (from 99.5% down to 95% or "
        "lower), increased raw material consumption per ton of acid, SO2 emissions exceeding "
        "environmental permit limits, and eventual catalyst replacement costing tens of "
        "thousands of dollars per bed."
    ))

    _body_bold(pdf, "Fault 5 -- Converter Thermal Runaway")
    _body(pdf, (
        "Mechanism: The oxidation of SO2 to SO3 releases 99 kJ per mole of SO2 converted. If "
        "the inter-bed heat exchangers fail to remove this heat adequately, the gas temperature "
        "rises entering the next bed. Since the reaction rate follows the Arrhenius equation, "
        "a higher temperature produces a faster reaction, which releases more heat, which "
        "further raises the temperature -- a positive feedback loop known as thermal runaway. "
        "Unlike a nuclear reactor's prompt-critical excursion, this is a slow (minutes) but "
        "relentless process. Once the bed temperature exceeds approximately 600 degC, the "
        "V2O5 catalyst sinters irreversibly. The molten salt phase volatilises, the support "
        "structure collapses, and catalytic activity is permanently destroyed.\n\n"
        "Sensor signature: Converter bed temperature rising rapidly above 550 degC with a "
        "steep positive slope (several degC per minute). The temperature in the hottest bed "
        "exceeds the critical limit.\n\n"
        "Consequence: Complete destruction of the catalyst in the affected bed -- 7-14 day "
        "shutdown for replacement, loss of production worth hundreds of thousands of dollars "
        "per day, and cost of new catalyst (typically $10,000-20,000 per cubic metre)."
    ))

    _body_bold(pdf, "Fault 6 -- Inter-Bed Cooling Failure")
    _body(pdf, (
        "Mechanism: Between catalyst beds, shell-and-tube heat exchangers cool the partially "
        "reacted gas from approximately 500 degC down to the optimal inlet temperature of "
        "approximately 430 degC for the next bed. The cooling medium is typically boiler feed "
        "water, which generates high-pressure steam as it absorbs heat. If the cooling water "
        "supply is interrupted, if the tubes are fouled on either the gas or water side, or "
        "if the steam pressure becomes excessive, the exchanger duty falls. The gas enters "
        "the next bed hotter than designed.\n\n"
        "Chemical consequence: The higher inlet temperature has two effects. First, Le "
        "Chatelier's principle shifts the equilibrium away from SO3 formation -- conversion "
        "per pass falls. Second, the higher operating temperature accelerates catalyst "
        "sintering in the downstream beds, permanently reducing their activity. A mild cooling "
        "failure may go unnoticed for hours or days while the plant slowly loses efficiency.\n\n"
        "Sensor signature: Temperature elevated despite adequate feed rate, with a sustained "
        "upward trend. The temperature difference between consecutive beds (dT across the "
        "exchanger) decreases, indicating reduced heat removal.\n\n"
        "Consequence: Lower conversion per pass, higher recycle load, increased energy "
        "consumption, gradual catalyst degradation in downstream beds, and eventual loss of "
        "production capacity."
    ))
    _footer(pdf)

    # ── 5. Fault Summary ────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "5. Fault Analysis Summary", 1)
    _body(pdf, (
        "The following table summarises the six fault scenarios, their underlying chemical "
        "engineering principle, the sensor signature produced, and the primary industrial "
        "consequence."
    ))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 8)
    col_w = [26, 30, 28, 24, 62]
    headers = ["Fault", "Chem Eng Principle", "Sensor Pattern", "Confidence", "Industrial Consequence"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, _s(h), border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    rows = [
        ["Catalyst Bed\nPlugging", "Ergun equation\n(packed bed dP)", "dP up,\nflow down", "High if\ntrend aligns",
         "Lost production; bed\nscreening or replacement\nrequires 7-14 day shutdown"],
        ["Air Blower\nFailure", "Mass transfer\n(convective feed)", "Flow near 0,\ndP near 0", "High",
         "Complete production\nhalt; SO2 backflow and\ncorrosion risk"],
        ["Acid Pump\nCavitation", "Net Positive Suction\nHead (NPSH)", "Low oscillating\npressure", "Medium",
         "Impeller destruction;\npump failure; SO3\nemission to atmosphere"],
        ["Catalyst\nFouling", "Catalyst\ndeactivation kinetics", "Temp up,\nflow mild down", "High if\ntrend aligns",
         "Efficiency loss; SO2\nemissions; catalyst\nreplacement after\nweeks-months"],
        ["Thermal\nRunaway", "Arrhenius eqn\n(positive feedback)", "Temp > 550 degC,\nsteep rising slope", "High if\nslope steep",
         "Catalyst sintering;\npermanent bed destruction;\n7-14 day outage"],
        ["Inter-Bed\nCooling Failure", "Heat transfer\n(U coefficient)", "Temp up,\nflow normal", "High if\ntrend up",
         "Lower conversion;\ncatalyst degradation;\nincreased energy cost"],
    ]
    for row in rows:
        max_lines = max(cell.count("\n") + 1 for cell in row)
        h = 6 * max_lines
        for i, cell in enumerate(row):
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.rect(x, y, col_w[i], h)
            pdf.multi_cell(col_w[i], 5, _s(cell))
            pdf.set_xy(x + col_w[i], y)
        pdf.ln(h - 2)
    pdf.ln(4)
    _body(pdf, "Table 1: Summary of contact process fault signatures with chemical engineering basis.")
    _footer(pdf)

    # ── 6. Monitoring System ────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "6. Monitoring System Overview", 1)
    _body(pdf, (
        "The fault detection and monitoring logic described in this study is implemented in "
        "SentinelGUI, a desktop software dashboard written in Python. The system reads live "
        "sensor data from either a physical Arduino-based data acquisition unit or a built-in "
        "process simulator, classifies each reading against the threshold bands defined for "
        "the contact process, evaluates the six fault signatures against current values and "
        "short-term trends, and displays the results on a colour-coded operator interface."
    ))
    _body(pdf, (
        "The chemical engineering knowledge incorporated in this work -- the Arrhenius equation "
        "for thermal runaway, the Ergun equation for bed plugging, NPSH analysis for cavitation, "
        "catalyst deactivation kinetics for fouling, and heat transfer analysis for cooling "
        "failure -- forms the diagnostic rule base that enables the system to distinguish between "
        "faults that may present with overlapping sensor patterns. The system also generates "
        "session summary reports documenting all alarms and diagnoses."
    ))
    _body(pdf, (
        "To run the contact process demonstration:"
    ))
    _body(pdf, (
        "  pip install -r sentinelgui/requirements.txt\n"
        "  python -m sentinelgui --simulate --kiosk --scenario contact"
    ))
    _body(pdf, (
        "This launches the dashboard with the contact process scenario, requiring no "
        "specialised hardware and no network connection. All diagnostic logic operates fully "
        "offline."
    ))
    _footer(pdf)

    # ── 7. Conclusion ───────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "7. Conclusion", 1)
    _body(pdf, (
        "The sulfuric acid contact process is a mature, thermodynamically complex industrial "
        "operation in which narrow temperature windows, reversible exothermic reaction kinetics, "
        "and expensive catalyst materials create significant operational risk. This study has "
        "examined six process fault scenarios arising in the contact process -- catalyst bed "
        "plugging, air blower failure, acid pump cavitation, catalyst fouling, converter "
        "thermal runaway, and inter-bed cooling failure -- each grounded in fundamental chemical "
        "engineering principles including Arrhenius reaction kinetics, packed-bed hydrodynamics "
        "(Ergun equation), vapour-liquid equilibrium (NPSH analysis), catalyst deactivation "
        "kinetics, and heat transfer through fouled exchanger surfaces."
    ))
    _body(pdf, (
        "By monitoring three critical process variables -- converter bed temperature, SO2 feed "
        "rate, and column pressure drop -- and evaluating them against these chemical engineering "
        "mechanisms, the SentinelGUI system demonstrates how software-based real-time monitoring "
        "can provide early warning of process deterioration, enable informed operator response, "
        "and help prevent the economic and safety consequences of uncontrolled fault development. "
        "The approach is general and can be extended to other chemical process operations where "
        "similar first-principles analysis can distinguish between competing fault mechanisms."
    ))
    _footer(pdf)

    # ── References ──────────────────────────────────────────────────────
    pdf.add_page()
    _heading(pdf, "References", 1)
    refs = [
        "1. C.N. Satterfield, Heterogeneous Catalysis in Industrial Practice, 2nd ed., McGraw-Hill, 1991.",
        "2. O. Levenspiel, Chemical Reaction Engineering, 3rd ed., Wiley, 1999.",
        "3. R.B. Bird, W.E. Stewart, E.N. Lightfoot, Transport Phenomena, 2nd ed., Wiley, 2002.",
        "4. S. Ergun, 'Fluid Flow through Packed Columns,' Chemical Engineering Progress, vol. 48, pp. 89-94, 1952.",
        "5. M.P. Cooke, E.W. Martin, 'Contact Process for Sulfuric Acid Manufacture,' in Kirk-Othmer Encyclopedia of Chemical Technology, Wiley, 2001.",
        "6. P. Trambouze, J.P. Euzen, Chemical Reactors: From Design to Operation, Editions Technip, 2004.",
        "7. J.H. Gary, G.E. Handwerk, M.J. Kaiser, Petroleum Refining: Technology and Economics, 5th ed., CRC Press, 2007.",
        "8. F.A. Zenz, D.F. Othmer, Fluidization and Fluid-Particle Systems, Reinhold, 1960.",
    ]
    pdf.set_font("Helvetica", "", 9)
    for ref in refs:
        pdf.multi_cell(0, 5, _s(ref))
        pdf.ln(1)
    _footer(pdf)

    # ── Output ──────────────────────────────────────────────────────────
    filename = "sentinelgui_exhibition.pdf"
    filepath = str(Path(output_dir) / filename)
    pdf.output(filepath)
    return filepath


if __name__ == "__main__":
    path = generate()
    print(f"Exhibition PDF generated: {path}")
