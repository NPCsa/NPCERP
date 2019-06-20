from datetime import datetime, timedelta

from odoo import models, api


class hr_notification(models.Model):
    _name = 'hr.notification'

    @api.model
    def mail_remainder(self):
        for record in self.env['hr.employee'].search([]):
            date_now = datetime.now().date()
            if record.iqama_date_of_expiry:
                iqama = datetime.strptime(str(record.iqama_date_of_expiry), "%Y-%m-%d").date()
                notify_date = iqama - timedelta(4 * 365 / 12)
                if date_now == notify_date:
                    record.send_email_iqama()
            if record.passport_date_of_expiry:
                passport = datetime.strptime(str(record.passport_date_of_expiry), "%Y-%m-%d").date()
                notify_date_pass = passport - timedelta(5 * 365 / 12)
                if date_now == notify_date_pass:
                    record.send_email_passport()
            if record.trail_to:
                trail_period = datetime.strptime(str(record.trail_to), "%Y-%m-%d").date()
                notify_date_trial = trail_period - timedelta(days=14)
                if date_now == notify_date_trial:
                    record.send_email_trail()
            Contract = self.env['hr.contract']
            for contract in Contract.search([('employee_id', '=', record.id)]):
                if contract.date_end:
                    date_end_c = datetime.strptime(str(contract.date_end), "%Y-%m-%d").date()
                    notify_date_contract = date_end_c - timedelta(3 * 365 / 12)
                    if date_now == notify_date_contract:
                        record.send_email_contract()
            for insurance in record.insurance_ids:
                if insurance.end_date:
                    date_end_insurance = datetime.strptime(str(insurance.end_date), "%Y-%m-%d").date()
                    notify_date_insurance = date_end_insurance - timedelta(4 * 365 / 12)
                    if date_now == notify_date_insurance:
                        record.send_email_insurance()
            for company in self.env['res.company'].search([]):
                if company.commercial_date:
                    date_end_comm = datetime.strptime(str(company.commercial_date), "%Y-%m-%d").date()
                    notify_date_com = date_end_comm - timedelta(4 * 365 / 12)
                    if date_now == notify_date_com:
                        company.send_email_com()
                if company.municipal_date:
                    date_end_mu = datetime.strptime(str(company.municipal_date), "%Y-%m-%d").date()
                    notify_date_mu = date_end_mu - timedelta(4 * 365 / 12)
                    if date_now == notify_date_mu:
                        company.send_email_mu()


hr_notification()
