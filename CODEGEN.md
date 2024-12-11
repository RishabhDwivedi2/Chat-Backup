`CodeGen Manual` 
`v0.0.0`

1.	Please note this manual is about CodeGen. 
2.	There is a separate manual about DevOps automation (currently WIP) for deploying code via local, development, UAT, staging and production environments, using GitHub, Docker, CircleCI.
3.	As with everything AI, due to fast paced innovations, this CodeGen Manual will be continually updated. This manual takes into consideration capabilities and tools available as of Oct 2, 2024. 

_________________________________________

The CodeGen process leverages the following **AI tools** for development efficiency and code quality:
    1.	Cursor IDE (AI Chat Feature, note Composer Workflow is still WIP), using Claude 3.5 Sonnet as the main coding  model.
    2.	Claude Website (primarily to brainstorm with the full context of the project available in the Claude Projects Knowledge Base).
    3.	OpenAI ChatGPT (o1-preview). This is used to due its high reasoning capabilities. In effect, the output of Claude would usually be artifact memos, which are then used as inputs for 01-preview for critical analysis, if second opinion is needed. 
    4.	v0.dev by Vercel for UI development. 

_________________________________________

`A. AI Engineering Foundational Best Practices`

1.	`Context is Paramount`

CodeGenAI is only as good as the prompt, which means the better the input, i.e., context, the better the response. 

    a.	When developing a new feature, tag for better context:
        Tag : @tech_stack.md`
        Tag : @project_tree.md + @api_specs.md + @database_schema.md
        Tag : @code_feature_frontend.md or @code_feature_backend.md
        Tag : @frontend/src or @backend/app (or be more precise, if you can)
        Tag : @{feature}_plan.md + @{feature}_checklist.md (more on this later in this manual)

    b.	Clearly explain what you are looking for. If you think your input is not clear, as a first step ask Cursor Chat to repeat your instructions for clarity. 
    c.	Then, using the checklist as the guidance, ask AI to implement one element at a time. 
    d.	When debugging, in addition to the error that you will tag to the Cursor Chat, tag @edit_frontend_code.md or @edit_backend_code.md so that you get very precise an actionable response. You may need to tag @project_tree.md to ensure that errors related to import statements can be fixed correctly. 

*Note about import statements: Currently developing (WIP) a script that will be deployed at runtime to auto fix the import statements in the code.* 

2.	`Use .WIP`

At times, Cursor may alter parts of the code that were not intended to be changed, leading to bugs or regressions. Why does this happen?
    a.	Asking Cursor to refactor the code and it may make some fundamental changes. 
    b.	Asking Cursor to improve one function, and it may make changes to another function or functions thinking them to be  linked with each other and therefore require changes.
    c.	When fixing an error, at times, Cursor makes certain assumptions, based on which it gives the solutions.  These assumptions may not be aligned to the CodeGen project tree or tech stack or specific requirements.  The result is a non-desired response, which if applied will result in bugs and regressions. 

To avoid this from happening, do the following:
    a.	Create a .wip/ directory to work on copies of files that you are currently editing. This way the unedited files are available in the .wip/ directory to be easily reverted. 
    b.	Clearly define the scope of changes needed, specifying which files or functions should be modified.
    c.	Do not apply change without reviewing them manually. A quick review of the diff is enough. If any undesired changes are being suggested, reject one or all of them and ask Cursor to re generated the response with the constraints mentioned by you. 

3.	`Plans & Checklists` 

AIs work best when directed well. Best way to direct an AI is to have it work out a plan and execute on a check list. 

**a. For a new feature:** 

    1. If a totally new feature is being developed, it is worthwhile to brainstorm in great detail best plan of action to develop that feature. For this use Claude. 

    2. To use Claude effectively, create a project within Claude called {feature}. To the project knowledge base by adding these files from your local drive repo: 
    `@tech_stack.md`,  @project_tree.md, @api_specs.md, @database_schema.md, 
    @code_feature_frontend.md, @code_feature_backend.md

    3. Outcome of this exercise should be @{feature}_plan.md + @{feature}_checklist.md.  
    Add these files to the {feature} project knowledge base with Claude in case you need to revisit. Whether to take the code from Claude or not, you will learn from experience. Generally, it is better not to take the Code from Claude. But if you do, ensure you take the code in .md files. 

    4. Download and upload these files to the .\workspace\plans_checklist\{feature} directory of your project for AI be use them further. 

    5. If you think, that a second opinion may make the plan/checklist/code more robust, get it from ChatGPT (o1-preview). Ensure you give the proper context to ChatGPT. Giving proper context will require to upload all relevant files. It is worthwhile to get a second opinion in case of planning totally new/complex feature. 

    6. Again, ask ChatGPT to give the output in downloadable .md files. Upload these also to the .\workspace\plans_checklist\{feature} directory. 

**b. For enhancing an existing feature:** 
    1. In this particular case, you would have the existing @{feature}_plan.md and @feature_checklist.md available with you already.
    2. If it is a minor enhancement, follow the .wip process and ask Cursor Chat to modify the plan and checklist and implement it within Cursor itself.
    3. If it is a major feature, follow the new feature development process.  

`4.	Backups`

In case AI tools introduce errors or corrupt files, backups ensure you can restore the previous working state.
    •	Manual Backups: Run backup_manual.py before significant changes.
    •	Automatic Backups: Keep backup_auto.py running during development.
    •	Use the .wip/ Directory: Work on copies of files to prevent accidental overwrites.

`5.	UI Development `

In case of a new feature, you will need a new UI or changes may be required the existing one.

*Foundational UI*
    1.	Use v0.dev by Vercel to develop the foundational UI, i.e., the very first UI for the project. 
    Add @tech_stack.md and {feature}_plan.md and {feature}_checklist.md files to provide proper context to v0. 

    2.	If developing the foundational UI, ensure that in addition the basic layout and landing page, v0 also provides the global.css file (to import into the project and also for future use)
    3.	Once you are satisfied with the design, npx the code as a component into the project. It will become part of the .\frontend\src\components directory. It will have a snake-case name. 
    4.	Copy this file as well as the @project_tree.md file into .wip folder.

    5.	Then, ask Cursor Chat by tagging @project_tree.md, whether new directories and files are needed to implement the code in .\..\components\{feature}, which was developed by v0. If yes, then create those directories and folders. 
        i.	Suggest to follow PascalCase in naming your components to distinguish from the snake-case component file name developed by v0.
        ii.	Also, suggest to breakdown the component in multiple small files if you think, any of them can be reused. 

    6.	Then, with an updated @project_tree.md file, ask Cursor Chat to split the v0 developed file into the update project tree files, taking special care of the import statements. 

*Additional UI Component*
    1.	Follow the above process but all give v0 @api_specs.md and @database_schema.md files so that v0 can develop the frontend UI using the contents of those files. 

`B. Work flows`

1.	New Feature Development 
    a.	Brainstorm with Claude, and if needed, with ChatGPT. 
    b.	Develop UI with v0.
    c.	Conduct backup operations. 
    d.	Import the UI into the project and split the code into relevant files. 
    e.	Ask Cursor Chat to develop backend code (tag .\frontend\src\lib\api.ts if available).
    f.	If any changes have been made to a file in the .\backend\app\models directory, then do a migration using the python scripts\database\alembic_new_migration.py script. 
    g.	Once bugs if any have been fixed, take a manual backup using python scripts\backups\backup_manual.py. 
    h.	Alternatively, if you have already developed the backend first, then ensure .\frontend\src\lib\api.ts file on the frontend is appropriate updated. 

2.	Using a third party repo or code 
    a.	Import third party code in a separate directory or file. 
    b.	Copy the relevant files in the .wip directory.
    c.	Then, follow the same process for a new feature development set forth above. 
 
3.	Debugging Existing Code
    a.	As mentioned, following the .wip process for file editing. 
