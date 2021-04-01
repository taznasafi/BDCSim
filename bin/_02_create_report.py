from BDCSim import BDCSim, os


def create_report(run=True):

    reporter = BDCSim.Simulator()
    reporter.output_folder = os.path.join(reporter.base_output_folder, 'csv')

    if run:
        reporter.report()