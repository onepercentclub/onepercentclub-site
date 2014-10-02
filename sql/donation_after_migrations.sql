
alter table payments_orderpayment drop constraint order_id_refs_id_120d56a7;
ALTER TABLE payments_orderpayment ADD CONSTRAINT order_id_refs_id FOREIGN KEY (order_id) REFERENCES orders_order (id)

