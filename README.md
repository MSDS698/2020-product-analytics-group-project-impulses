# 2020-product-analytics-group-project-impulses

## Deployment Resources

Master branch url: http://impulse-master.eba-2mxduspm.us-west-2.elasticbeanstalk.com/

Test branch url: http://imp-env-test-3.eba-ri85ihii.us-west-2.elasticbeanstalk.com/ 

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

