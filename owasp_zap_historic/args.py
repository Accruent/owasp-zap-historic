"""This module controls the command line arguments for OWASP ZAP Historic."""
import argparse


def parse_options():
    """This is the overall command line module for owaspzaphistoric"""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    general = parser.add_argument_group("General")

    general.add_argument(
        '-s', '--sqlhost',
        dest='sqlhost',
        default='localhost',
        help="MySQL database host address"
    )

    general.add_argument(
        '-t', '--sqlport',
        dest='sqlport',
        default='3306',
        help="MySQL database port"
    )

    general.add_argument(
        '-u', '--username',
        dest='username',
        default='superuser',
        help="User name of MySQL database"
    )

    general.add_argument(
        '-p', '--password',
        dest='password',
        default='passw0rd',
        help="Password of MySQL database"
    )

    general.add_argument(
        '-a', '--apphost',
        dest='apphost',
        default='0.0.0.0',
        help="Flask app host address"
    )

    args = parser.parse_args()
    return args
