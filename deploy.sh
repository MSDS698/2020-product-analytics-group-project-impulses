# Create environment
echo "3\n\nImpulses_script\nY\n1\nn\nn\n" | eb init -i
eb create imp-env-test
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
eb terminate
aws elasticbeanstalk delete-application --application-name Impulses_script
aws codepipeline delete-pipeline --name Impulses_script