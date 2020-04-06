# Scenarios

## Climate scenarios

## Management scenarios (including prices)

In each scenario json file, scenario-relevant info that is expected to extend/update the base json model file is defined. For example, the following would be used to define alternative price scenarios:
```json
{
    "scenarios": [
        {
            "name": "Price Year",
            "size": 2
        }
    ],
    "parameters": {
        "Price Year": {
            "type": "ConstantScenario",
            "scenario": "Price Year",
            "values": [
                2009,
                2045
            ]
        }
    }
}
```

One or more scenario definitions like the above can be included in a single model run by modifying the `scenario_sets.json` file. For example, three studies, with three different scenarios included, could be defined as follows:
 
```json
{
    "energy_prices_study": {
        "name": "Energy Prices",
        "scenarios": ["energy_prices"]
    },
    "functional_flows_study": {
        "name": "Functional Flows",
        "scenarios": ["functional_flows"]
    },
    "full_study": {
        "name": "Functional flows with future energy prices",
        "scenarios": ["energy_prices", "functional_flows"]
    }
}
```