"""Word document — Sulfuric Acid Contact Process exhibition document.

Generates a .docx file suitable for chemical technology exhibition.
Requires python-docx: pip install python-docx

Usage:
    python -m sentinelgui.exhibition_docx

Output: sentinelgui_exhibition.docx in the project root.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


def _add_heading(doc, text: str, level: int = 1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x14, 0x28, 0x50)
    return h


def _add_body(doc, text: str):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.3
    for run in p.runs:
        run.font.size = Pt(11)
    return p


def _add_bold_para(doc, text: str):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(2)
    return p


def _add_table(doc, headers: list[str], rows: list[list[str]], col_widths: list[float] | None = None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shading = cell._element.get_or_add_tcPr()
        shading_fill = shading.makeelement(qn('w:shd'), {
            qn('w:val'): 'clear',
            qn('w:color'): 'auto',
            qn('w:fill'): '142850',
        })
        shading.append(shading_fill)

    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = val
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
            if r_idx % 2 == 1:
                shading = cell._element.get_or_add_tcPr()
                fill = shading.makeelement(qn('w:shd'), {
                    qn('w:val'): 'clear',
                    qn('w:color'): 'auto',
                    qn('w:fill'): 'f0f4f8',
                })
                shading.append(fill)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()
    return table


def generate(output_dir: str = ".") -> str:
    doc = Document()

    # Default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # ── Title page ──────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    run = p.add_run("Real-Time Process Monitoring for the\nSulfuric Acid Contact Process")
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(0x14, 0x28, 0x50)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("A Chemical Technology Perspective on Fault Detection and Safety")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x00, 0x90, 0x9E)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Chemical Technology Exhibition")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

    doc.add_page_break()

    # ── Members ─────────────────────────────────────────────────────────
    _add_heading(doc, "Project Members", 1)
    doc.add_paragraph()
    _add_table(doc, ["GR No", "Name"], [
        ["", "Muhammad Usman Bin Shamim"],
        ["", ""],
        ["", ""],
    ], col_widths=[5, 10])

    _add_heading(doc, "Contents", 1)
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
    for item in toc:
        p = doc.add_paragraph(item, style='List Number')
        for run in p.runs:
            run.font.size = Pt(11)

    doc.add_page_break()

    # ── Abstract ────────────────────────────────────────────────────────
    _add_heading(doc, "Abstract", 1)
    _add_body(doc, (
        "Sulfuric acid (H2SO4) is the most-produced chemical by volume worldwide, with annual "
        "output exceeding 250 million metric tons. The dominant production route is the contact "
        "process, in which sulfur is burned to sulfur dioxide, catalytically oxidised to sulfur "
        "trioxide over vanadium pentoxide (V2O5), and absorbed in concentrated sulfuric acid. The "
        "catalytic oxidation step -- 2SO2 + O2 <-> 2SO3 -- is exothermic (dH = -99 kJ/mol) and "
        "reversible, requiring precise temperature control between 400 and 450 degC to maintain "
        "both high reaction rate and favourable equilibrium conversion."
    ))
    _add_body(doc, (
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

    doc.add_page_break()

    # ── 1. Introduction ─────────────────────────────────────────────────
    _add_heading(doc, "1. Introduction", 1)
    _add_body(doc, (
        "Sulfuric acid is a foundational chemical commodity. Its primary application is in the "
        "manufacture of phosphate fertilisers, which consume approximately 60% of global production. "
        "Other major uses include petroleum refining (alkylation catalysts), metal ore leaching "
        "(copper, uranium, zinc), industrial water treatment, and the production of dyes, "
        "pigments, detergents, and pharmaceuticals. The scale of production and the hazardous "
        "nature of the materials involved make process safety a paramount concern."
    ))

    _add_bold_para(doc, "The Contact Process")
    _add_body(doc, (
        "The contact process, commercialised in the late 19th century by the German chemical "
        "industry and refined continuously since, is today the universally adopted method for "
        "sulfuric acid manufacture. The process consists of three chemically distinct stages:"
    ))
    _add_body(doc, (
        "Stage 1 -- Combustion of elemental sulfur:\n"
        "   S(s) + O2(g) -> SO2(g),   dH = -297 kJ/mol\n"
        "   Molten sulfur is sprayed into a combustion furnace with dried air at approximately "
        "1000 degC. The reaction is highly exothermic and self-sustaining once ignited. The "
        "resulting gas stream contains roughly 8-12% SO2 by volume, with the balance being N2, "
        "excess O2, and trace combustion products."
    ))
    _add_body(doc, (
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
    _add_body(doc, (
        "Stage 3 -- Absorption of SO3:\n"
        "   SO3(g) + H2O(l) -> H2SO4(l),   dH = -130 kJ/mol\n"
        "   Sulfur trioxide cannot be absorbed directly in water, as the reaction forms a dense "
        "acid mist that is difficult to capture. Instead, SO3 is absorbed in circulating "
        "concentrated sulfuric acid (98-99% H2SO4), which reacts to form additional H2SO4. The "
        "product acid is continuously withdrawn and diluted with water to the desired "
        "concentration."
    ))

    _add_bold_para(doc, "Why monitoring matters")
    _add_body(doc, (
        "Each stage of the contact process operates under tightly constrained conditions. "
        "Deviation from the optimal temperature window in the catalytic converter reduces "
        "conversion efficiency and risks permanent catalyst damage. Feed rate imbalances can "
        "create explosive gas mixtures or cause environmental SO2 emissions. Cooling system "
        "failures can initiate thermal runaway. Real-time monitoring of key process variables "
        "is not merely an operational convenience but a fundamental safety requirement, analogous "
        "to the trip systems and interlocks found in all modern chemical process plants."
    ))

    # ── 2. Thermodynamics and Kinetics ────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "2. Thermodynamics and Kinetics of the Catalytic Oxidation", 1)

    _add_bold_para(doc, "Equilibrium considerations")
    _add_body(doc, (
        "The oxidation of SO2 to SO3 is exothermic and reversible. Le Chatelier's principle "
        "predicts that lower temperatures favour the forward (product-forming) reaction, while "
        "higher temperatures favour the reverse decomposition. The equilibrium constant Kp for "
        "the reaction decreases with increasing temperature:"
    ))
    _add_body(doc, "   log10(Kp) = 5186/T - 0.611*log10(T) + 6.750")
    _add_body(doc, (
        "where T is in Kelvin. At 400 degC (673 K), Kp is approximately 380; at 500 degC "
        "(773 K), Kp falls to approximately 40. This strong temperature dependence means that "
        "even modest overheating of a catalyst bed can significantly reduce the per-pass "
        "conversion."
    ))

    _add_bold_para(doc, "Reaction kinetics")
    _add_body(doc, "The rate of SO2 oxidation over V2O5 catalyst follows the Arrhenius equation:")
    _add_body(doc, "   k = A * exp(-Ea / RT)")
    _add_body(doc, (
        "where k is the rate constant, A is the pre-exponential factor (approximately "
        "3 x 10^5 s^-1 for commercial V2O5 catalysts), Ea is the activation energy "
        "(approximately 90-110 kJ/mol for the V2O5-catalysed reaction), R is the universal "
        "gas constant (8.314 J/mol.K), and T is absolute temperature."
    ))
    _add_body(doc, (
        "Doubling the temperature from 400 degC to 500 degC increases the reaction rate by "
        "a factor of approximately 10, but simultaneously halves the equilibrium conversion. "
        "This tension between rate and conversion is resolved industrially by employing "
        "multiple catalyst beds with inter-bed cooling: the gas reacts partially in the first "
        "bed, is cooled, reacts further in the second bed, and so on. Modern converters "
        "typically have four or five beds, achieving overall conversions exceeding 99.5%."
    ))

    _add_bold_para(doc, "Catalyst structure and deactivation")
    _add_body(doc, (
        "The industrial catalyst consists of 6-8% V2O5 promoted with alkali metal sulfates "
        "(typically K2SO4 or Cs2SO4) and supported on diatomaceous silica. The active phase is "
        "a molten salt melt of alkali pyrosulfates (M2S2O7) that wets the support surface. "
        "SO2 and O2 dissolve in this melt and react to form SO3, which then desorbs into the "
        "gas phase."
    ))
    _add_body(doc, (
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

    # ── 3. Process Monitoring Parameters ───────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "3. Process Monitoring Parameters", 1)
    _add_body(doc, (
        "Three process variables provide a complete picture of converter health and are "
        "continuously monitored in real time:"
    ))

    _add_bold_para(doc, "3.1 Converter Bed Temperature (degC)")
    _add_body(doc, (
        "The temperature at the hottest point in each catalyst bed is the single most important "
        "indicator of converter condition. The normal operating range is 400-450 degC, with "
        "the peak temperature occurring just downstream of the bed inlet where the reaction "
        "rate is highest. A rising temperature trend indicates that the exothermic reaction is "
        "accelerating -- either because the inlet gas is too hot (inter-bed cooling failure) or "
        "because the catalyst activity has declined and the plant has increased the feed "
        "temperature to compensate (catalyst fouling). A falling temperature suggests feed "
        "interruption or excessively cold inlet gas."
    ))

    _add_bold_para(doc, "3.2 SO2 Feed Rate (L/min)")
    _add_body(doc, (
        "The volumetric flow rate of SO2 entering the converter determines the production rate "
        "and must be maintained within strict limits relative to the available oxygen. The "
        "stoichiometric O2:SO2 ratio for the oxidation reaction is 0.5:1, but industrial "
        "practice uses excess oxygen (typically 1.5:1 to 2:1) to drive the equilibrium toward "
        "product. If the feed rate drops, production falls proportionally. If the feed rate "
        "rises above the design capacity of the converter, the residence time becomes "
        "insufficient for complete reaction."
    ))

    _add_bold_para(doc, "3.3 Column Pressure Drop (dP) in bar")
    _add_body(doc, "The pressure drop follows the Ergun equation for packed beds:")
    _add_body(doc, "   dP/L = 150 * (1-e)^2/e^3 * mu*V / Dp^2 + 1.75 * (1-e)/e^3 * rho*V^2 / Dp")
    _add_body(doc, (
        "A rising dP indicates decreasing bed void fraction -- caused by dust accumulation, "
        "catalyst attrition fines, or sintered deposits. This is an early warning of bed "
        "plugging. A falling dP with falling flow rate indicates blower or feed failure."
    ))

    # ── 4. Fault Detection ──────────────────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "4. Fault Detection in the Contact Process", 1)
    _add_body(doc, (
        "Six distinct process fault scenarios can be identified from the sensor signatures. Each "
        "fault is described below in terms of its chemical engineering mechanism, the resulting "
        "sensor pattern, and the industrial consequence if left unaddressed."
    ))

    faults = [
        ("Fault 1 -- Catalyst Bed Plugging",
         "Fine particulate matter from the sulfur combustion furnace (ash, unburned sulfur dust) "
         "or catalyst attrition debris accumulates in the interstitial spaces between catalyst "
         "pellets. The bed void fraction decreases, causing the pressure drop to rise per the "
         "Ergun equation, while the flow resistance reduces volumetric throughput.",
         "Column dP rises progressively while SO2 feed rate declines. The ratio dP/flow increases "
         "above normal.",
         "Reduced production rate. If plugging continues, the bed may require screening or full "
         "replacement -- a 7-14 day shutdown involving cooling, catalyst handling, and significant "
         "labour and material cost."),

        ("Fault 2 -- Air Blower Failure",
         "The main air blower or SO2 circulator trips or loses power. Without forced draught, "
         "gas flow through the converter stops. The catalytic reaction ceases immediately because "
         "reactants cannot reach the catalyst surface -- the process is mass-transfer-limited.",
         "Feed rate collapses to near zero. Column pressure equalises to atmospheric (dP approaches "
         "zero). Temperatures across the beds fall as the exotherm extinguishes.",
         "Complete production halt. Risk of SO2 backflow into air ducts and acid condensation in "
         "cold sections, causing corrosion. Blower restart must account for potential explosive "
         "atmospheres."),

        ("Fault 3 -- Acid Pump Cavitation",
         "In the absorption tower circuit, if the static pressure at the pump suction falls below "
         "the vapour pressure of the circulating acid, vapour bubbles nucleate at the impeller eye "
         "and collapse violently against the blade surfaces. Net Positive Suction Head (NPSH) "
         "available drops below NPSH required.",
         "Low, oscillating pressure in the acid circulation line with significantly higher variance "
         "than normal operation.",
         "Progressive mechanical destruction of the pump impeller, pump failure, loss of acid "
         "circulation, SO3 breakthrough to atmosphere, environmental emission violation."),

        ("Fault 4 -- Catalyst Fouling and Poisoning",
         "Impurities in the feed gas -- particularly arsenic trioxide (As2O3) from sulfur "
         "feedstocks -- gradually interact with the active vanadium species, forming stable "
         "arsenate complexes (V2O5.As2O3) that have no catalytic activity. Operators compensate "
         "by raising inlet temperature, accelerating sintering of remaining active surface.",
         "Converter temperature rises slowly over days to weeks as the plant increases firing. "
         "Feed rate may drop mildly from incipient bed restriction.",
         "Reduced SO2-to-SO3 conversion efficiency (from 99.5% down to 95% or lower), increased "
         "raw material consumption, SO2 emissions exceeding environmental permits, eventual "
         "catalyst replacement."),

        ("Fault 5 -- Converter Thermal Runaway",
         "The oxidation of SO2 to SO3 releases 99 kJ/mol. If inter-bed heat exchangers fail, "
         "temperature rises, accelerating the reaction rate per the Arrhenius equation -- a "
         "positive feedback loop. Above 600 degC, V2O5 catalyst sinters irreversibly: the molten "
         "salt phase volatilises, support collapses, and activity is permanently destroyed.",
         "Converter bed temperature rising rapidly above 550 degC with a steep positive slope "
         "(several degC per minute). The hottest bed exceeds the critical limit.",
         "Complete catalyst bed destruction -- 7-14 day shutdown for replacement, loss of "
         "production worth hundreds of thousands of dollars per day, catalyst cost of "
         "$10,000-20,000 per cubic metre."),

        ("Fault 6 -- Inter-Bed Cooling Failure",
         "Shell-and-tube heat exchangers between catalyst beds cool partially reacted gas from "
         "approximately 500 degC to the optimal 430 degC for the next bed. If cooling water is "
         "insufficient or tubes are fouled, gas enters the next bed too hot. Le Chatelier's "
         "principle shifts equilibrium away from SO3, and higher temperatures accelerate "
         "catalyst sintering in downstream beds.",
         "Temperature elevated despite adequate feed rate, with sustained upward trend. The "
         "temperature difference across the exchanger decreases.",
         "Lower conversion per pass, higher recycle load, increased energy consumption, gradual "
         "catalyst degradation in downstream beds."),
    ]

    for title, mechanism, signature, consequence in faults:
        _add_bold_para(doc, title)
        p = doc.add_paragraph()
        run = p.add_run("Mechanism: ")
        run.bold = True
        run.font.size = Pt(11)
        run = p.add_run(mechanism)
        run.font.size = Pt(11)

        p = doc.add_paragraph()
        run = p.add_run("Sensor signature: ")
        run.bold = True
        run.font.size = Pt(11)
        run = p.add_run(signature)
        run.font.size = Pt(11)

        p = doc.add_paragraph()
        run = p.add_run("Consequence: ")
        run.bold = True
        run.font.size = Pt(11)
        run = p.add_run(consequence)
        run.font.size = Pt(11)
        doc.add_paragraph()

    # ── 5. Fault Summary Table ──────────────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "5. Fault Analysis Summary", 1)
    _add_body(doc, (
        "The following table summarises the six fault scenarios, their underlying chemical "
        "engineering principle, the sensor signature produced, and the primary industrial "
        "consequence."
    ))

    _add_table(doc,
        ["Fault", "Chem Eng Principle", "Sensor Pattern", "Confidence", "Industrial Consequence"],
        [
            ["Catalyst Bed Plugging", "Ergun equation (packed bed dP)", "dP up, flow down",
             "High if trend aligns", "Lost production; bed replacement requires 7-14 day shutdown"],
            ["Air Blower Failure", "Mass transfer (convective feed)", "Flow near 0, dP near 0",
             "High", "Complete production halt; SO2 backflow risk"],
            ["Acid Pump Cavitation", "NPSH (vapour pressure)", "Low oscillating pressure",
             "Medium", "Impeller destruction; pump failure; SO3 emission"],
            ["Catalyst Fouling", "Catalyst deactivation kinetics", "Temp up, flow mild down",
             "High if trend aligns", "Efficiency loss; SO2 emissions; catalyst replacement"],
            ["Thermal Runaway", "Arrhenius eqn (positive feedback)", "Temp >550 degC, steep slope",
             "High if slope steep", "Catalyst destroyed; 7-14 day outage"],
            ["Inter-Bed Cooling Failure", "Heat transfer (U coefficient)", "Temp up, flow normal",
             "High if trend up", "Low conversion; catalyst degradation"],
        ]
    )

    # ── 6. Physical Demonstration Model ─────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "6. Physical Demonstration Model", 1)
    _add_body(doc, (
        "A non-functional physical model of the sulfuric acid contact process was constructed on a "
        "thermocol (styrofoam) sheet to serve as a visual teaching aid alongside the software "
        "dashboard. The model depicts the major unit operations of the contact process in their "
        "sequential order, with each component hand-painted and labelled for clarity."
    ))
    _add_body(doc, (
        "The model layout includes the following stages arranged left to right: Sulfur Burner "
        "(combustion chamber) connected by a flow path arrow to the Multi-Bed Catalytic Converter "
        "(with visible inter-bed cooling sections), then to the Absorption Tower, and finally to "
        "the Acid Storage Tank. Each stage is colour-coded -- red for the high-temperature "
        "combustion section, orange for the catalytic converter, blue for the absorption and "
        "cooling sections, and yellow for the final acid product. Arrows indicate the direction "
        "of gas and liquid flow through the process. The thermocol base is mounted on a display "
        "board with an information panel summarising the chemical reactions at each stage."
    ))

    # ── 7. Monitoring System Overview ──────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "7. Monitoring System Overview", 1)
    _add_body(doc, (
        "The fault detection and monitoring logic described in this study is implemented in "
        "SentinelGUI, a desktop software dashboard written in Python. The system reads live "
        "sensor data from either a physical Arduino-based data acquisition unit or a built-in "
        "process simulator, classifies each reading against the threshold bands defined for "
        "the contact process, evaluates the six fault signatures against current values and "
        "short-term trends, and displays the results on a colour-coded operator interface."
    ))
    _add_body(doc, (
        "The chemical engineering knowledge incorporated in this work -- the Arrhenius equation "
        "for thermal runaway, the Ergun equation for bed plugging, NPSH analysis for cavitation, "
        "catalyst deactivation kinetics for fouling, and heat transfer analysis for cooling "
        "failure -- forms the diagnostic rule base that enables the system to distinguish between "
        "faults that may present with overlapping sensor patterns. The system also generates "
        "session summary reports documenting all alarms and diagnoses."
    ))
    _add_body(doc, (
        "To run the contact process demonstration:\n\n"
        "   pip install -r sentinelgui/requirements.txt\n"
        "   python -m sentinelgui --simulate --kiosk --scenario contact\n\n"
        "This launches the dashboard with the contact process scenario, requiring no "
        "specialised hardware and no network connection. All diagnostic logic operates fully "
        "offline."
    ))

    # ── 8. Conclusion ───────────────────────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "8. Conclusion", 1)
    _add_body(doc, (
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
    _add_body(doc, (
        "By monitoring three critical process variables -- converter bed temperature, SO2 feed "
        "rate, and column pressure drop -- and evaluating them against these chemical engineering "
        "mechanisms, the SentinelGUI system demonstrates how software-based real-time monitoring "
        "can provide early warning of process deterioration, enable informed operator response, "
        "and help prevent the economic and safety consequences of uncontrolled fault development. "
        "The approach is general and can be extended to other chemical process operations where "
        "similar first-principles analysis can distinguish between competing fault mechanisms."
    ))

    # ── References ──────────────────────────────────────────────────────
    doc.add_page_break()
    _add_heading(doc, "References", 1)
    refs = [
        "C.N. Satterfield, Heterogeneous Catalysis in Industrial Practice, 2nd ed., McGraw-Hill, 1991.",
        "O. Levenspiel, Chemical Reaction Engineering, 3rd ed., Wiley, 1999.",
        "R.B. Bird, W.E. Stewart, E.N. Lightfoot, Transport Phenomena, 2nd ed., Wiley, 2002.",
        "S. Ergun, 'Fluid Flow through Packed Columns,' Chemical Engineering Progress, vol. 48, pp. 89-94, 1952.",
        "M.P. Cooke, E.W. Martin, 'Contact Process for Sulfuric Acid Manufacture,' in Kirk-Othmer Encyclopedia of Chemical Technology, Wiley, 2001.",
        "P. Trambouze, J.P. Euzen, Chemical Reactors: From Design to Operation, Editions Technip, 2004.",
        "J.H. Gary, G.E. Handwerk, M.J. Kaiser, Petroleum Refining: Technology and Economics, 5th ed., CRC Press, 2007.",
        "F.A. Zenz, D.F. Othmer, Fluidization and Fluid-Particle Systems, Reinhold, 1960.",
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph(f"{i}. {ref}")
        for run in p.runs:
            run.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(2)

    # ── Output ──────────────────────────────────────────────────────────
    filename = "sentinelgui_exhibition.docx"
    filepath = str(Path(output_dir) / filename)
    doc.save(filepath)
    return filepath


if __name__ == "__main__":
    path = generate()
    print(f"Word document generated: {path}")
