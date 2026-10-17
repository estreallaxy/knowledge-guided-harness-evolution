# SCOPE : Scalable COde Planning Engine
![SCOPE Workflow](src/main_diagram.svg "SCOPE Workflow")

SCOPE is a multi-agent framework that systematically converts natural language queries into optimized structured representations, capturing both combination and constraint parameters. These representations are then used to generate reusable solver functions, enabling consistent, efficient, and reliable execution of diverse problem-solving tasks across the same domain. Specifically, we construct three functions :
* Combination Function: Generates candidate plans from the combination parameters.
* Filter Function: Selects plans that satisfy all constraint parameters.
* Deliver Function: Converts the filtered plan into a natural language answer in the desired format.
