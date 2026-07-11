# EcoRoute: Carbon Tax Optimization Dashboard

EcoRoute is a smart tracking dashboard built for anyone tackling the daily Mississauga commute. I designed it to take the guesswork out of travel costs: it visualizes your route, calculates your carbon tax savings, and maps out a 5-year comparison between driving and taking transit. Plus, it features a built-in AI transit strategist to give you real-time, neighborhood-specific advice.

## Features

* **Interactive Geographic Mapping:** Tracks explicit high-density snapped road vectors between regional Mississauga transit hubs (UTM, Square One, Port Credit GO, Erin Mills Town Centre) using `folium`.
* **Live "Optimization Wallet":** A 3-column real-time tracking display that calculates weekly/annual carbon tax saved, $CO_2$ avoided, and equivalent tree-days of environmental mitigation.
* **5-Year Macroeconomic Cost Projections:** A compounding line chart visualizing variable regional fuel pricing configurations against fixed municipal transit fares over a five-year horizon.
* **AI Commute Strategist:** Utilizes serverless open-source model inference (`deepseek-ai/DeepSeek-V3-0324` via Featherless.ai) to generate tailored, hyper-local spatial logistics and infrastructure advice.

---

## Tech Stack

* **Frontend & Framework:** Streamlit
* **Geospatial Visualization:** Folium, Streamlit-Folium
* **Data Manipulation:** Pandas
* **AI Inference Engine:** Featherless.ai API (OpenAI Python SDK Client)
* **Language & Environment:** Python 3.11

---

## Calculations
* **Carbon Tax Savings Formula**

Driving costs scale directly with a vehicle's baseline efficiency. The system calculates single-trip tax penalties using a custom emissions multiplier:

$$Single\ Trip\ Tax\ Saved = Distance\ (km) \times 0.15 \times \left(\frac{Vehicle\ Emission\ Factor\ (g/km)}{200.0}\right)$$

* **Environmental Mitigation Modeling**

To compute the mass of greenhouse gases prevented by choosing public transit over a personal vehicle, the dashboard measures the delta against a baseline passenger transit footprint:

$$Weekly\ CO_2\ Avoided\ (kg) = \frac{\left(Vehicle\ Emission\ Factor - Transit\ Factor\right) \times Distance \times Weekly\ Trips}{1000}$$

---

## Project Structure

```text
├── .streamlit/
│   └── config.toml         # Streamlit server and security configurations
├── app.py                  # Main application source code
├── README.md               # Project documentation
├── requirements.txt        # Python dependency manifest
└── runtime.txt             # Deployment runtime environment file
```
