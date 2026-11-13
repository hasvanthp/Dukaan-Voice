create extension if not exists "pgcrypto";

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid unique,
  full_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists stores (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references users(id) on delete restrict,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  name text not null,
  sku text,
  purchase_price numeric(12,2) not null check (purchase_price >= 0),
  selling_price numeric(12,2) not null check (selling_price >= 0),
  unit text not null,
  stock_qty numeric(12,3) not null default 0 check (stock_qty >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  name text not null,
  phone text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(store_id, phone)
);

create table if not exists customer_credits (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  customer_id uuid not null references customers(id) on delete cascade,
  outstanding_balance numeric(12,2) not null default 0,
  updated_at timestamptz not null default now(),
  unique(store_id, customer_id)
);

create table if not exists sales (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  customer_id uuid references customers(id) on delete set null,
  total_amount numeric(12,2) not null check (total_amount >= 0),
  total_profit numeric(12,2) not null,
  paid_amount numeric(12,2) not null default 0,
  idempotency_key text not null,
  created_by uuid references users(id),
  created_at timestamptz not null default now(),
  unique(store_id, idempotency_key)
);

create table if not exists sale_items (
  id uuid primary key default gen_random_uuid(),
  sale_id uuid not null references sales(id) on delete cascade,
  product_id uuid not null references products(id) on delete restrict,
  quantity numeric(12,3) not null check (quantity > 0),
  unit_price numeric(12,2) not null check (unit_price > 0)
);

create table if not exists inventory_movements (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  product_id uuid not null references products(id) on delete restrict,
  change_qty numeric(12,3) not null,
  movement_type text not null,
  reason text,
  idempotency_key text,
  created_by uuid references users(id),
  created_at timestamptz not null default now(),
  unique(store_id, idempotency_key)
);

create table if not exists payments (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  customer_id uuid not null references customers(id) on delete restrict,
  amount numeric(12,2) not null check (amount > 0),
  mode text not null,
  note text,
  idempotency_key text not null,
  created_by uuid references users(id),
  created_at timestamptz not null default now(),
  unique(store_id, idempotency_key)
);

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  user_id uuid references users(id) on delete set null,
  language text not null default 'hinglish',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists conversation_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  role text not null check (role in ('user','assistant','system')),
  content text not null,
  intent text,
  confidence numeric(4,3),
  created_at timestamptz not null default now()
);

create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  store_id uuid not null references stores(id) on delete cascade,
  actor_user_id uuid references users(id),
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_products_store on products(store_id);
create index if not exists idx_inventory_store_product on inventory_movements(store_id, product_id, created_at desc);
create index if not exists idx_sales_store_created on sales(store_id, created_at desc);
create index if not exists idx_payments_store_customer on payments(store_id, customer_id, created_at desc);
create index if not exists idx_conversations_store on conversations(store_id, updated_at desc);
create index if not exists idx_messages_conversation on conversation_messages(conversation_id, created_at);
create index if not exists idx_audit_store_created on audit_events(store_id, created_at desc);

alter table stores enable row level security;
alter table products enable row level security;
alter table customers enable row level security;
alter table customer_credits enable row level security;
alter table sales enable row level security;
alter table sale_items enable row level security;
alter table inventory_movements enable row level security;
alter table payments enable row level security;
alter table conversations enable row level security;
alter table conversation_messages enable row level security;
alter table audit_events enable row level security;

create or replace function current_store_uuid() returns uuid
language sql stable as $$
  select nullif(current_setting('request.jwt.claim.store_id', true), '')::uuid
$$;

create policy stores_by_owner on stores
for all using (owner_user_id in (select id from users where auth_user_id = auth.uid()));

create policy products_by_store on products
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy customers_by_store on customers
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy credits_by_store on customer_credits
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy sales_by_store on sales
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy movements_by_store on inventory_movements
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy payments_by_store on payments
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy conversations_by_store on conversations
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());
create policy audit_by_store on audit_events
for all using (store_id = current_store_uuid()) with check (store_id = current_store_uuid());

create policy sale_items_by_store on sale_items
for all using (
  exists (
    select 1 from sales s where s.id = sale_items.sale_id and s.store_id = current_store_uuid()
  )
);

create policy messages_by_store on conversation_messages
for all using (
  exists (
    select 1 from conversations c where c.id = conversation_messages.conversation_id and c.store_id = current_store_uuid()
  )
);
