I want to build a new library that I intent to release as a PyPi package.

The goal is to make a package that users can easily install and use to spin up different Databricks solutions to get started quickly when building certains projects.

Help me come up with a good name for it. I am thinking maybe "databricks-industry-accelerators" or something similar. Give me other suggestions and also what the abbreviated version would then be - like "dia ..." or ?

These projects could include things like:

- Medallion architecture using notebooks (Spark notebooks + job for orchestration)
- Medallion arcitecture using declarative pipeline (SDP + job for orchestration)
- Dashboard
- Genie Space
- Mlflow project
- App (different tools like Streamlit, Flask, Dash, Node.js, etc.)
- Maybe data models for certain popular systems like Dynamics365, SAP, Salesforce, etc.?
- And possibly more...

I also want to include a SKILL.md file so that users can use their LLM to help them use the tool. This should support the most common agent like Copilot, Claude, Codex, etc.

I also want to make an industry spin on it. Finance reporting might be different than building an operational app that you might want to run more real-time. Help me refine this part - what industries would make sense to include and how? Maybe the products (like dashboards, apps, genie space is not too different, but the data model differs depending on the chosen industry).

I imagine that users use the tool through a CLI interface and that the AI agents will also use this. Help me refine this part as well - How to best do this? Maybe one way to do this would be "dia setup finance-reporting-dashboard" or what is best practice?

I want to provide good documentation and maybe build a github pages docs site using zensical?

For most of the accelerators, I want to have a really good framework for generating fake data in formats that users can redefine themselves. This would allow users to generate realistic, synthetic data. In simple examples, the Databricks sample datasets could maybe be used. I prefer to use Spark Custom Data sources for this since it can be used in both notebooks and SDP.

I want the solutions to be deployed to Databricks Free or normal workspaces. The default method should be using Databricks automation bundles, so that users can build real production products using this.