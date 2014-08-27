-- 1%Club Migration to Bluebottle donations

-- ORDERS
-- drop table orders_order;
alter table fund_order rename to "orders_order";
alter table orders_order add column "total" numeric(16,2);
alter table orders_order drop column recurring;
alter table orders_order drop column order_number;

--- DONATIONS
alter table fund_donation rename to "donations_donation";
alter table donations_donation add column "anonymous" boolean;
alter table donations_donation add column "completed" date;
alter table donations_donation alter column "amount" set data type numeric(12,2);
update donations_donation set amount = (amount /100);

--- FUNDRAISERS
alter table donations_donation alter column "amount" set data type numeric(12,2);
update fundraisers_fundraiser set amount = amount / 100;


--- WALLPOSTS
update wallposts_systemwallpost set related_type_id = (select id from django_content_type where app_label = 'donations');

