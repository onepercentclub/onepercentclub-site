-- 1%Club Migration to Bluebottle donations

-- ORDERS
-- drop table orders_order;
alter table fund_order rename to "orders_order";
alter table orders_order add column "total" numeric(16,2);

--- DONATIONS
alter table fund_donation rename to "donations_donation";
alter table donations_donation add column "anonymous" boolean;
alter table donations_donation add column "completed" date;
update donations_donation set amount = (amount /100);

