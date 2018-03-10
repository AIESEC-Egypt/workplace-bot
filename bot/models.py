from __future__ import unicode_literals

import csv
import datetime

from django.db import models


# Create your models here.

class DAAL(models.Model):
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    product = models.CharField(max_length=128, null=True, blank=True)


def parse_prefix(line, fmt):
    try:
        t = datetime.datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.datetime.strptime(line, fmt)
        else:
            raise
    return t


def process_daal(product, start_date, end_date):
    count = 0
    countries = []
    with open('DAAL.csv', 'r') as f:
        for row in csv.reader(f.read().splitlines()):
            countries.append(row[2])
        countries = set(countries)
        listofzeros = [0] * len(countries)
        # print countries
        countries = tuple(zip(countries, listofzeros))

    with open('DAAL.csv', 'r') as f:
        for row in csv.reader(f.read().splitlines()):
            if product[1:] == row[8]:
                print(row[2])
                for index, item in enumerate(countries):
                    country, count_of_country = item
                    if country == row[2]:
                        count_of_country = count_of_country + 1

                        start_date = datetime.datetime(year=2017, month=4, day=1)
                        end_date = datetime.datetime(year=2017, month=5, day=1)
                        # if (product == 'IGV'):
                        if start_date < parse_prefix(row[19], '%Y-%m-%d') < end_date:
                            count += 1
        print(countries)
        print(count)


class BasicAnalytic(models.Model):
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Applications numbers in each program

    ogv_applications = models.IntegerField(default=0)
    igv_applications = models.IntegerField(default=0)
    ogt_applications = models.IntegerField(default=0)
    igt_applications = models.IntegerField(default=0)
    oge_applications = models.IntegerField(default=0)
    ige_applications = models.IntegerField(default=0)

    # Approved numbers in each Program

    ogv_approved = models.IntegerField(default=0)
    igv_approved = models.IntegerField(default=0)
    ogt_approved = models.IntegerField(default=0)
    igt_approved = models.IntegerField(default=0)
    oge_approved = models.IntegerField(default=0)
    ige_approved = models.IntegerField(default=0)

    # Realized numbers in each Program
    ogv_realized = models.IntegerField(default=0)
    igv_realized = models.IntegerField(default=0)
    ogt_realized = models.IntegerField(default=0)
    igt_realized = models.IntegerField(default=0)
    oge_realized = models.IntegerField(default=0)
    ige_realized = models.IntegerField(default=0)

    # Finished numbers in each Program
    ogv_finished = models.IntegerField(default=0)
    igv_finished = models.IntegerField(default=0)
    ogt_finished = models.IntegerField(default=0)
    igt_finished = models.IntegerField(default=0)
    oge_finished = models.IntegerField(default=0)
    ige_finished = models.IntegerField(default=0)

    # Complete numbers in each Program
    ogv_completed = models.IntegerField(default=0)
    igv_completed = models.IntegerField(default=0)
    ogt_completed = models.IntegerField(default=0)
    igt_completed = models.IntegerField(default=0)
    oge_completed = models.IntegerField(default=0)
    ige_completed = models.IntegerField(default=0)

    # Total numbers in each Program
    total_applications = models.IntegerField(default=0)
    total_approved = models.IntegerField(default=0)
    total_realized = models.IntegerField(default=0)
    total_finished = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)

    def construct_analytics_message(self):
        return "This is the analytics for the Entity with ID {0} starting from {1} till {2}.".format(self.id, str(
            self.start_date), str(self.end_date)) + \
               "\n\nApplications :\nOGV - {0}\nOGT - {1}\nOGE - {2}\nIGV - {3}\nIGT - {4}\nIGE - {5}\nTotal - {6}".format(
                   self.ogv_applications, self.ogt_applications, self.oge_applications,
                   self.igv_applications, self.igt_applications, self.ige_applications,
                   self.total_applications) + \
               "\n\nApprovals :\nOGV - {0}\nOGT - {1}\nOGE - {2}\nIGV - {3}\nIGT - {4}\nIGE - {5}\nTotal - {6}".format(
                   self.ogv_approved, self.ogt_approved, self.oge_approved,
                   self.igv_approved, self.igt_approved, self.ige_approved,
                   self.total_approved) + \
               "\n\nRealizations :\nOGV - {0}\nOGT - {1}\nOGE - {2}\nIGV - {3}\nIGT - {4}\nIGE - {5}\nTotal - {6}".format(
                   self.ogv_realized, self.ogt_realized, self.oge_realized,
                   self.igv_realized, self.igt_realized, self.ige_realized,
                   self.total_realized) + \
               "\n\nFinished :\nOGV - {0}\nOGT - {1}\nOGE - {2}\nIGV - {3}\nIGT - {4}\nIGE - {5}\nTotal - {6}".format(
                   self.ogv_finished, self.ogt_finished, self.oge_finished,
                   self.igv_finished, self.igt_finished, self.ige_finished,
                   self.total_finished) + \
               "\n\nCompleted Experiences :\nOGV - {0}\nOGT - {1}\nOGE - {2}\nIGV - {3}\nIGT - {4}\nIGE - {5}\nTotal - {6}".format(
                   self.ogv_completed, self.ogt_completed, self.oge_completed,
                   self.igv_completed, self.igt_completed, self.ige_completed,
                   self.total_completed)


class AccessToken(models.Model):
    value = models.TextField()

    def __str__(self):
        return 'Access Token ' + str(self.id)

    class Meta:
        verbose_name = 'Access Token'
        verbose_name_plural = 'Access Token'


class CoreUser(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    initiated_conversation = models.BooleanField(default=False)
    first_question = models.BooleanField(default=False)
    second_question = models.BooleanField(default=False)
    third_question = models.BooleanField(default=False)

    path = models.CharField(max_length=128, blank=True, null=True)

    first_question_daal = models.BooleanField(default=False)
    second_question_daal = models.BooleanField(default=False)
    third_question_daal = models.BooleanField(default=False)

    basic_analytic = models.OneToOneField(BasicAnalytic, related_name="basic_analytic", on_delete=models.CASCADE,
                                          blank=True, null=True)
    relative_analytic = models.OneToOneField(BasicAnalytic, related_name="relative_analytic", on_delete=models.CASCADE,
                                             blank=True, null=True)
    daal = models.OneToOneField(DAAL, on_delete=models.CASCADE, blank=True, null=True)

    def restart_process(self):
        self.initiated_conversation = False
        self.first_question = False
        self.second_question = False
        self.third_question = False
        self.basic_analytic = None
        self.save()

    def restart_process_daal(self):
        self.initiated_conversation = False
        self.first_question_daal = False
        self.second_question_daal = False
        self.third_question_daal = False
        self.daal = None
        self.save()
