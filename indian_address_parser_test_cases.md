# Indian Address Parser — 20 Messy Address Test Cases

**Dataset composition:** 20 cases total — **13 sourced real addresses** and **7 synthetic stress tests**.

**Purpose:** Evaluate extraction and normalization of Indian address components such as building/house, street, locality, village, landmark, post office (P.O.), police station (P.S.), block, tehsil, district, state and PIN code.

---

# Part A — Real sourced addresses (13)

## REAL-01 — Bankura district office / C/O structure

**Raw input**

```text
C/O District Magistrate & Collector, Bankura, Administrative Building, 2nd Floor, P.O. & Dist. Bankura, PIN 722101
```

**Challenge focus:** `C/O` relationship; office/building/floor hierarchy; one place name serving as both post-office and district reference.

**Source:** [Electoral Registration Officers — West Bengal (PDF)](https://www.hcikl.gov.in/pdf/ERO_withDetails_sent_to_Commission_westbengal.pdf) — address listed for the Barjora constituency's ERO.

## REAL-02 — Bishnupur sub-divisional office

**Raw input**

```text
C/O Sub-divisional Officer, Bishnupur, Administrative Building, P.O. Bishnupur, Dist. Bankura. PIN 722122
```

**Challenge focus:** `C/O`; administrative designation versus recipient/location; P.O. and district in different positions.

**Source:** [Electoral Registration Officers — West Bengal (PDF)](https://www.hcikl.gov.in/pdf/ERO_withDetails_sent_to_Commission_westbengal.pdf) — address listed for the Bishnupur constituency.

## REAL-03 — Burdwan Collectorate

**Raw input**

```text
Burdwan Collectorate Administrative Building 2nd Floor PO & Dist – Burdwan Pin – 713101
```

**Challenge focus:** Missing commas; floor/building sequence; `PO`, `Dist` and `Pin` abbreviations; en dash punctuation.

**Source:** [Electoral Registration Officers — West Bengal (PDF)](https://www.hcikl.gov.in/pdf/ERO_withDetails_sent_to_Commission_westbengal.pdf) — address listed for the Khandaghosh constituency.

## REAL-04 — Mahipur electricity distribution office

**Raw input**

```text
MAHIPUR, NEAR BARAHAR MORE, P.O.- MAHIPUR, P.S.- KUMARGANJ, DIST.- DAKSHIN DINAJPUR, PIN- 733141
```

**Challenge focus:** Landmark before postal hierarchy; locality and P.O. repeat; P.S. differs from P.O.; heavily abbreviated administrative labels.

**Source:** [WBSEDCL — District Dakshin Dinajpur, Government of West Bengal](https://ddinajpur.nic.in/wbsedcl-2/) — Kumarganj CCC address.

## REAL-05 — Patiram electricity distribution office

**Raw input**

```text
UTSAB BHABAN (GROUND FLOOR), P.O.- PATIRAM, P.S.- PATIRAM, DIST.- DAKSHIN DINAJPUR. PIN- 733133
```

**Challenge focus:** Building name and floor in parentheses; P.O. and P.S. share the same name; mixed comma/full-stop separators.

**Source:** [WBSEDCL — District Dakshin Dinajpur, Government of West Bengal](https://ddinajpur.nic.in/wbsedcl-2/) — Patiram CCC address.

## REAL-06 — Gangarampur electricity distribution office

**Raw input**

```text
BLOCK PARA, NEAR B.D. OFFICE, P.O.- GANGARAMPUR, P.S.- GANGARAMPUR, DIST.- DAKSHIN DINAJPUR. PIN- 733124
```

**Challenge focus:** Locality and landmark; abbreviated landmark (`B.D. OFFICE`); repeated P.O./P.S. name; district abbreviation.

**Source:** [WBSEDCL — District Dakshin Dinajpur, Government of West Bengal](https://ddinajpur.nic.in/wbsedcl-2/) — Gangarampur CCC address.

## REAL-07 — Head Quarters Fire Station, Kolkata

**Raw input**

```text
13D, Mirza Ghalib Street, P.O. New Market, P.S. New Market, Kolkata - 16. Landmark:- Free School Street Fire Station
```

**Challenge focus:** Street number attached to building number; P.O. and P.S. share a name; legacy shortened PIN suffix (`Kolkata - 16`); landmark appears at the end.

**Source:** [West Bengal Fire & Emergency Services — Communication Strategy document](https://wbfes.gov.in/webomagic/getFile?fid=2244&view=true), updated 04 April 2024 — Head Quarters Fire Station listing.

## REAL-08 — Garden Reach Fire Station

**Raw input**

```text
71/1, Garden Reach Road, Kolkata 700043. P.S - West Port, Land Mark : Infront of West Port P.S.
```

**Challenge focus:** House/street number with slash; PIN embedded before police-station details; landmark repeats the P.S. name; inconsistent spacing and punctuation.

**Source:** [West Bengal Fire & Emergency Services — Communication Strategy document](https://wbfes.gov.in/webomagic/getFile?fid=2244&view=true), updated 04 April 2024 — Garden Reach Fire Station listing.

## REAL-09 — Alifnagar Fire Station

**Raw input**

```text
C.G.Road, Kolkata - 700024, P.S.- West Port, P.O.- Garden Reach, Landmark.- near FOJ (GRSE unit).
```

**Challenge focus:** P.S. and P.O. are different; abbreviation-heavy street/landmark; acronym in parentheses; mixed punctuation.

**Source:** [West Bengal Fire & Emergency Services — Communication Strategy document](https://wbfes.gov.in/webomagic/getFile?fid=2244&view=true), updated 04 April 2024 — Alifnagar Fire Station listing.

## REAL-10 — Masterda Surya Sen Fire Station

**Raw input**

```text
BANSDRONI GOVT. COLONY, P.O + P.S - BANSDRONI, KOLKATA - 700070. NEAREST LANDMARK - KALIBARI BRIDGE
```

**Challenge focus:** Combined P.O. + P.S. notation; `GOVT.` abbreviation; landmark in uppercase; locality and postal town sequence.

**Source:** [West Bengal Fire & Emergency Services — Communication Strategy document](https://wbfes.gov.in/webomagic/getFile?fid=2244&view=true), updated 04 April 2024 — Masterda Surya Sen Fire Station listing.

## REAL-11 — Ranchi establishment listing with repeated road/locality details

**Raw input**

```text
443/A, ROAD NO.5, ASHOK NAGAR,RANCHI-834002, JHARKHAND, BLOCK: RANCHI(CR), P.O.: ASHOK NAGAR, S.O. POST OFFICE, RANCHI-834002, P.S.: ARGORA POLICE STATION, ROAD NO.2, ASHOK NAGAR, DIST.: RANCHI, PIN: 834002
```

**Challenge focus:** Multiple road references; repeated Ashok Nagar and Ranchi; PIN appears twice; P.O. expands to a sub-office description; P.S. field contains its own road detail.

**Source:** [Jharkhand Comprehensive Labour Management System — establishment listing](https://shramadhan.jharkhand.gov.in/CLMS/futureInspectionList.action) — address recorded for an establishment in Ashok Nagar, Ranchi.

## REAL-12 — Harsinghraidih establishment listing

**Raw input**

```text
VILL: HARSINGHRAIDIH, LANDMARK: DUKHIA MAHADEO ROAD, BLOCK: GIRIDIH, P.O.: BUDHIADIH, P.S.: GIRIDIH (M), DIST.: GIRIDIH, PIN: 815302
```

**Challenge focus:** Village and landmark; block/P.O./P.S./district sequence; P.S. suffix in parentheses; locality names that differ across administrative levels.

**Source:** [Jharkhand Comprehensive Labour Management System — establishment listing](https://shramadhan.jharkhand.gov.in/CLMS/futureInspectionList.action) — address recorded for an establishment in Giridih.

## REAL-13 — Bongaigaon Refinery mailing address

**Raw input**

```text
Chief Manager (MS, T&D), T&D Section, Indian Oil Corporation Ltd, Bongaigaon Refinery, P.O. Dhaliagaon, Dist : Chirang, Assam PIN – 783385
```

**Challenge focus:** Recipient/title and department mixed with the physical address; organization and facility hierarchy; punctuation and spacing around district/PIN labels.

**Source:** [Indian Oil Corporation — Bongaigaon Refinery apprenticeship notification (PDF)](https://iocl.com/download/Notification-engagement-apprentices-Bongaigaon-Refinery.pdf) — postal address in the application instructions (2016 notification).

---

# Part B — Synthetic stress tests (7)

> The following addresses are invented test fixtures. Names and PIN-like values are placeholders, not verified locations or postal codes.

## SYN-14 — Unordered apartment address with route-style directions

**Raw input**

```text
flat B-702 aster residency phase 2 7th cross behind old water tank take lane next to sai provision store second left green park ext ward 18 po devnagar ps north circle block navpur dist nandipur rajasthan 000000
```

**Intended challenge:** Unordered components; direction-based landmark chain; `ext` abbreviation; several administrative levels; invalid placeholder PIN.

## SYN-15 — C/O plus conflicting lane/house references

**Raw input**

```text
c/o R K Sharma h no 44/2 gali 6 (new gali 3?) near hanuman chowk opp old PHC village keshopur post keshopur BO PS kotwali rural tehsil naya nagar dist madhopur UP pin 123456
```

**Intended challenge:** C/O person; parenthetical correction/uncertainty; `opp`, `PHC`, `BO`, `PS`; village and post-office name repeated; synthetic PIN.

## SYN-16 — Shop above/inside a market with landmark pile-up

**Raw input**

```text
shop no 12 first floor municipal market bus stand ke saamne near old SBI branch opposite petrol pump main road ward 9 PO basantpur PS basantpur dist devgarh CG 999999
```

**Intended challenge:** Mixed English/Hinglish; shop and floor; multiple landmarks; P.O. and P.S. same name; synthetic PIN.

## SYN-17 — Rural address with several administrative layers

**Raw input**

```text
makan 3 govt middle school ke piche pani tank ke paas village amdiha post badhgaon PS city kotwali block lakhanpur tehsil bhairavpur zila surajgarh jharkhand pin 111111
```

**Intended challenge:** Transliteration; landmark phrases; rural village/post/block/tehsil/district hierarchy; `zila` synonym for district; synthetic PIN.

## SYN-18 — Typo-like PIN and ambiguous post-office phrase

**Raw input**

```text
plot 88 sector 4 shree ganesh nagar phase 2 near canal bridge opposite temple PO same as village? shreenagar police station industrial area district navgarh karnataka 5600O1
```

**Intended challenge:** Uncertain P.O. statement; sector/locality; competing police-station and industrial-area phrases; letter `O` inside a PIN-like string — do not silently convert it to zero.

## SYN-19 — Highway/warehouse address with distance directions

**Raw input**

```text
c/o manager suryodaya warehouse gate 3 service road NH 44 opposite toll plaza approx 5 km after railway crossing village nandipur PO nandipur PS highway dist dhanora telangana 500000
```

**Intended challenge:** Recipient role; facility/gate; highway and service road; relative-distance directions; village and P.O. repeat; synthetic PIN.

## SYN-20 — Two addresses accidentally pasted together

**Raw input**

```text
old address house 9 ward 2 PO chandpur dist east nandipur pin 765432; NEW address flat 203 sai arcade ring road near city bus depot PO lakshmi nagar PS central district nandipur odisha pin 765432
```

**Intended challenge:** Detect two separate address records; old/new labels; different localities and administrative data; same PIN-like value repeated. Do not merge the two addresses.

---

