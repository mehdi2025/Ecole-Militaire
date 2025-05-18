import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import coverage

if __name__ == "__main__":
    # Configure Django settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'CollegeERP.settings'
    django.setup()
    
    # Start code coverage
    cov = coverage.Coverage(
        source=['info', 'apis'],
        omit=['*/migrations/*', '*/tests/*', '*/admin.py']
    )
    cov.start()
    
    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(["tests"])
    
    # Generate coverage report
    cov.stop()
    cov.save()
    
    print('Coverage Report:')
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='coverage_html')
    print('HTML report generated in coverage_html directory')
    
    # Generate XML report for SonarQube
    cov.xml_report(outfile='coverage.xml')
    print('XML report generated as coverage.xml')
    
    sys.exit(bool(failures))

