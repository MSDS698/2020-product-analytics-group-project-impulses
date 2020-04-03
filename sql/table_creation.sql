--*****************************************************
--create table "dw"."category"
DROP TABLE IF EXISTS "dw"."category";

CREATE TABLE "dw"."category"
(
 "category_id"   bigserial NOT NULL,
 "category_desc" varchar NOT NULL,
 CONSTRAINT "PK_category" PRIMARY KEY ( "category_id" )
);


--*****************************************************
--create table "dw"."user"
DROP TABLE IF EXISTS "dw"."user";

CREATE TABLE "dw"."user"
(
 "user_id"     bigserial NOT NULL,
 "auth_id"     varchar NOT NULL,
 "first_name"  varchar NOT NULL,
 "last_name"   varchar NOT NULL,
 "email"       varchar NOT NULL,
 "phone"       bigint NOT NULL,
 "signup_date" date NOT NULL,
 "status"      varchar NOT NULL,
 CONSTRAINT "PK_Users" PRIMARY KEY ( "user_id" )
);


--*****************************************************
--create table "dw"."plaid_items"
DROP TABLE IF EXISTS "dw"."plaid_items";

CREATE TABLE "dw"."plaid_items"
(
 "plaid_id"     bigserial NOT NULL,
 "user_id"      bigint NOT NULL,
 "item_id"      varchar NOT NULL,
 "access_token" varchar NOT NULL,
 CONSTRAINT "PK_plaid_items" PRIMARY KEY ( "plaid_id" ),
 CONSTRAINT "FK_96" FOREIGN KEY ( "user_id" ) REFERENCES "dw"."user" ( "user_id" )
);
CREATE INDEX "fkIdx_96" ON "dw"."plaid_items"
(
 "user_id"
);


--*****************************************************
--create table "dw"."accounts"
DROP TABLE IF EXISTS "dw"."accounts";

CREATE TABLE "dw"."accounts"
(
 "account_id"       bigserial NOT NULL,
 "user_id"          bigint NOT NULL,
 "plaid_id"         bigint NOT NULL,
 "account_plaid_id" varchar NOT NULL,
 "account_name"     varchar NOT NULL,
 "account_type"     varchar NOT NULL,
 "account_subtype"  varchar NOT NULL,
 CONSTRAINT "PK_accounts" PRIMARY KEY ( "account_id" ),
 CONSTRAINT "FK_138" FOREIGN KEY ( "user_id" ) REFERENCES "dw"."user" ( "user_id" ),
 CONSTRAINT "FK_162" FOREIGN KEY ( "plaid_id" ) REFERENCES "dw"."plaid_items" ( "plaid_id" )
);
CREATE INDEX "fkIdx_138" ON "dw"."accounts"
(
 "user_id"
);
CREATE INDEX "fkIdx_162" ON "dw"."accounts"
(
 "plaid_id"
);


--*****************************************************
--create table "dw"."password"
DROP TABLE IF EXISTS "dw"."password";

CREATE TABLE "dw"."password"
(
 "password_id" bigserial NOT NULL,
 "user_id"     bigint NOT NULL,
 "password"    varchar NOT NULL,
 CONSTRAINT "PK_password" PRIMARY KEY ( "password_id" ),
 CONSTRAINT "FK_132" FOREIGN KEY ( "user_id" ) REFERENCES "dw"."user" ( "user_id" )
);
CREATE INDEX "fkIdx_132" ON "dw"."password"
(
 "user_id"
);


--*****************************************************
--create table "dw"."savings_history"
DROP TABLE IF EXISTS "dw"."savings_history";

CREATE TABLE "dw"."savings_history"
(
 "savings_id"        bigserial NOT NULL,
 "user_id"           bigint NOT NULL,
 "savings_amount"    decimal(10,2) NOT NULL,
 "total_savings"     decimal(10,2) NOT NULL,
 "predicted_savings" decimal(10,2) NULL,
 "transfer_date"     date NOT NULL,
 "update_date"       date NOT NULL,
 CONSTRAINT "PK_savings_history" PRIMARY KEY ( "savings_id" ),
 CONSTRAINT "FK_81" FOREIGN KEY ( "user_id" ) REFERENCES "dw"."user" ( "user_id" )
);
CREATE INDEX "fkIdx_81" ON "dw"."savings_history"
(
 "user_id"
);


--*****************************************************
--create table "dw"."transaction"
DROP TABLE IF EXISTS "dw"."transaction";

CREATE TABLE "dw"."transaction"
(
 "transaction_id"      bigserial NOT NULL,
 "user_id"             bigint NOT NULL,
 "account_id"          bigint NOT NULL,
 "trans_date"          date NOT NULL,
 "post_date"           date NOT NULL,
 "trans_amount"        decimal(10,2) NOT NULL,
 "merchant_category"   varchar NULL,
 "merchant_location"   varchar NULL,
 "category_id"         bigint NOT NULL,
 "is_preferred_saving" varchar NULL,
 CONSTRAINT "PK_Transactions" PRIMARY KEY ( "transaction_id" ),
 CONSTRAINT "FK_165" FOREIGN KEY ( "account_id" ) REFERENCES "dw"."accounts" ( "account_id" ),
 CONSTRAINT "FK_84" FOREIGN KEY ( "user_id" ) REFERENCES "dw"."user" ( "user_id" ),
 CONSTRAINT "FK_90" FOREIGN KEY ( "category_id" ) REFERENCES "dw"."category" ( "category_id" )
);
CREATE INDEX "fkIdx_165" ON "dw"."transaction"
(
 "account_id"
);
CREATE INDEX "fkIdx_84" ON "dw"."transaction"
(
 "user_id"
);
CREATE INDEX "fkIdx_90" ON "dw"."transaction"
(
 "category_id"
);


--*****************************************************
--check tables
select * from dw.category;

select * from dw.user;

select * from dw.plaid_items;

select * from dw.accounts;

select * from dw.password;

select * from dw.savings_history;

select * from dw.transaction;
