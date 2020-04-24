# 2020-product-analytics-group-project-impulses

## Pycodestyle
* pep8 test is now integrated as a part of github workflow and python code with style errors will not be able to merge into master
* If an codestyle error exist, clicking on the details will direct to the section of the code that displays style errors
* `./app/__init__.py` is removed from pep8 test on the github workflow as import statement in this file cannot be at the top of the file
* re-run `pycodestyle ./app/__init__.py` locally if any changes made to this file to make sure no other pycodestyle erro exists other than 2 `E402 module level import not at top of file` errors before pushing any changes

## Deployment Resources

Master branch url: http://impulses.us-west-2.elasticbeanstalk.com/

Test branch url: http://impulse-test.us-west-2.elasticbeanstalk.com/

AWS Codepipeline: https://aws.amazon.com/codepipeline/

## Testing Branch Usage Guidelines:
* Test branch should not be held for more than 20 minutes.

## How to test changes and deploy your branch?
* __Notify the team (@channel in #we_need_a_name) that test branch will be in use__
* sign-in to AWS console using your IAM account (sign in to console)
* go to `CodePipeline` service
* click on Impulse_test CodePipeline
* click on `Edit`
* edit stage for `Source` and update the branch to the branch you wish to deploy
* `save` the changes
* once changes are saved click on `Release Change` (This is important because CodePipeline only detect changes when something is being commited, changing source will not be automatically deployed)
* once `deploy` is finished, you should be able to view changes in the `Test branch url` linked above
* __Notify the team (@channel in #we_need_a_name) that test branch will NOT be in use__ 

