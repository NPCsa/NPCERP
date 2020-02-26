# -*- coding: utf-8 -*-

from odoo import api, models, _, fields
from odoo.exceptions import UserError


class Purchase_RequestOrder(models.Model):
    _name = 'purchase.request.order'
    _description = "Purchase Request Order"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Supplier", domain=[('supplier', '=', True)],
                                 required=True, )

    @api.multi
    def button_confirm(self, vals):
        """" create a purchase order for the selected purchase request """

        active_ids = vals.get('active_ids', []) or []
        lines = self.env['purchase.request'].browse(active_ids)
        approved_order = lines.filtered(lambda r: r.state == 'approved')
        if not approved_order:
            raise UserError(_("No Approved Lines or PO Exist"))
        po_object = self.env['purchase.order']
        list_lines = []
        for purchase_request in approved_order:
            error = ""
            for po_req_line in purchase_request.line_ids:
                purchase_req = po_req_line.request_id
                list_lines.append((0, 0, {'product_id': po_req_line.product_id.id,
                                          'product_qty': po_req_line.product_qty,
                                          'product_uom': po_req_line.product_id.uom_id.id,
                                          'price_unit': po_req_line.product_id.list_price,
                                          'name': po_req_line.name,
                                          'date_planned': po_req_line.date_required,
                                          'account_analytic_id': po_req_line.analytic_account_id.id}))
            purchase = po_object.create({
                "picking_type_id": purchase_req.picking_type_id.id,
                "company_id": purchase_req.company_id.id,
                "date_order": purchase_req.date_start,
                "partner_id": self.partner_id.id,
                "order_line": list_lines
            })
            for po_req_line in purchase_request.line_ids:
                po_req_line.update({'purchase_id': purchase.id})
        # if error:
        #     raise UserError(_(error))
        return True

    @api.multi
    def button_createPO(self, vals):
        """ Create a purchase order for the selected purchase request lines

            return bool, if true
                   else error message
        """
        active_ids = vals.get('active_ids', []) or []
        lines = self.env['purchase.request.line'].browse(active_ids)
        approved_lines = lines.filtered(
            lambda r: r.request_state == 'approved' and
                      not r.purchase_line_id)

        if not approved_lines:
            raise UserError(_("No Approved Lines or PO Exist"))
        error = ""
        po_object = self.env['purchase.order']
        list_lines = []
        for po_req_line in approved_lines:
            purchase_req = po_req_line.request_id
            list_lines.append((0, 0, {'product_id': po_req_line.product_id.id,
                                      'product_qty': po_req_line.product_qty,
                                      'product_uom': po_req_line.product_id.uom_id.id,
                                      'price_unit': po_req_line.product_id.list_price,
                                      'name': po_req_line.name,
                                      'date_planned': po_req_line.date_required,
                                      'account_analytic_id':po_req_line.analytic_account_id.id}))
        purchase = po_object.create({
            "picking_type_id": purchase_req.picking_type_id.id,
            "company_id": purchase_req.company_id.id,
            "date_order": purchase_req.date_start,
            "partner_id": self.partner_id.id,
            "order_line":list_lines
        })
        for po_req_line in approved_lines:
            po_req_line.update({'purchase_id': purchase.id})
        if error:
            raise UserError(_(error))
        return True

    def createPO(self, po_req_line, error):
        po_object = self.env['purchase.order']
        purchase_req = po_req_line.request_id
        if not self.partner_id.id:
            error += ("\n No Supplier for Request: " +
                      purchase_req.name + " Product: " +
                      po_req_line.name)
        else:
            purchase = po_object.search(
                [('partner_id', '=', self.partner_id.id),
                 ('state', '=', 'draft')
                 ], limit=1, order="id desc"
            )
            po_line = self.env['purchase.order.line']
            if purchase:
                po_line = po_line.search(
                    [('order_id', '=', purchase.id),
                     ('product_id', '=', po_req_line.product_id.id)
                     ], limit=1
                )
            else:
                purchase = po_object.create({
                    "picking_type_id": purchase_req.picking_type_id.id,
                    "company_id": purchase_req.company_id.id,
                    "date_order": purchase_req.date_start,
                    "partner_id": self.partner_id.id
                })
            if purchase and po_line:
                req_qty = po_line.product_qty + po_req_line.product_qty
                po_line.update({
                    'product_id': po_req_line.product_id.id,
                    'product_qty': req_qty,
                    'product_uom': po_req_line.product_id.uom_id.id,
                    'price_unit': po_req_line.product_id.list_price,
                    'name': po_req_line.name,
                    'date_planned': po_req_line.date_required,
                    'order_id': purchase.id
                })
            else:
                po_line = po_line.create({
                    'product_id': po_req_line.product_id.id,
                    'product_qty': po_req_line.product_qty,
                    'product_uom': po_req_line.product_id.uom_id.id,
                    'price_unit': po_req_line.product_id.list_price,
                    'name': po_req_line.name,
                    'date_planned': po_req_line.date_required,
                    'order_id': purchase.id
                })

            if po_line:
                po_req_line.update({'purchase_id': purchase.id,
                                    'purchase_line_id': po_line.id})
            else:
                error += (" \n No Order created for : " +
                          purchase_req.name + " Product: " +
                          po_req_line.name)
        return error
