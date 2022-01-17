# Endpoints

In this documents the endpoints are listed for each application.

## Netherlands

* [Albert Heijn](#albert-heijn)
* [Jumbo](#jumbo)
* [Picnic](#picnic)

### Albert Heijn

**BASE URL:** `https://api.ah.nl/` or `https://ms.ah.nl`

**BASE:** mobile-auth/
**BASE:** mobile-services/

POST

* v1/auth/token/anonymous
  * data:

  ```json
  {"clientId": "appie"}
  ```

* *v1/auth/token/bonuscard*
* *v1/auth/token/logout*
* *v1/auth/token*
* *v1/auth/token/refresh*
* *v1/auth/token/federate*
* *v1/auth/federate/code*

OTHER

* bonuspage/v1/activate/{offerId}
* bonuspage/v1/bonus-folder
* bonuspage/v1/choose-and-activate
* bonuspage/v1/delivery-bundle
* bonuspage/v1/metadata
* bonuspage/v1/personal
* bonuspage/v1/segment
* cms/v3/content/customerservice
* cms/v3/document
* cms/v3/notifications
* config/v1/features/android/
* discover/v1/backplate
* discover/v1/bonus
* discover/v2/deliveryincentives/group/{id}
* discover/v2/deliveryincentives/groups
* lists/v1/lists
* lists/v1/lists/{id}
* lists/v1/lists/{id}/items
* lists/v1/lists/{id}/items/{itemId}
* lists/v2/lists/{favoriteProductId}
* loyalty-lane/v1/entry-points
* loyalty-lane/v1/entry-points/overview
* loyaltycard/mmi-banner
* loyaltycard/v1
* loyaltycard/v1/{type}/{cardNumber}
* member/v3/bonus-card
* member/v3/member
* member/v3/member
* member/v3/membership
* member/v3/subscription
* member/v3/unsubscribe-blockers
* memos/v1/service-memos
* order/v1
* order/v1/items
* order/v1/summaries/active
* order/v1/summaries/latest
* order/v1/{orderId}/state
* order/v1/{orderId}/submit
* product/detail/v4/fir/{webShopId}
* product/search/v1/gtin/{barcode}
* product/search/v2
* product/search/v2/products
* product/search/v2/suggestions
* recipes/v1/favourite/ids
* recipes/v1/favourite/ids
* recipes/v1/favourite/ids/{recipeId}
* recipes/v1/mmi-banner-homepage
* recipes/v1/recipe/by-ids
* recipes/v1/recipe/{id}
* recipes/v1/recipe/{id}/ingredients
* recipes/v1/recipe/{id}/shoppable-ingredients
* recipes/v2/custom-lanes
* recipes/v2/favorites
* recipes/v2/magazine
* recipes/v2/search
* recipes/v2/sponsored-products-lane
* recipes/v2/top-recipes
* rules
* service
* sessions/{uuid}
* shoppinglist/v2/items
* shoppinglist/v2/shoppinglist
* stamps/v1/airmiles/balances
* stamps/v1/transfer
* stamps/v2/transactions
* stamps/v3/programs?returnFinishedCampaigns=true
* togo/v1/campaigns/balance
* trips/{uuid}
* trips/{uuid}/exitgate/status
* trips/{uuid}/items
* trips/{uuid}/items
* trips/{uuid}/items/{barcode}
* trips/{uuid}/items/{barcode}
* trips/{uuid}/payment/status
* trips/{uuid}/payment/totals
* v1/addresses/lookup
* v1/analytics
* v1/customer-care/channels
* v1/events
* v1/football-passion/clubs
* v1/football-passion/clubs
* v1/football-passion/donation
* v1/football-passion/lottery
* v1/football-passion/overview
* v1/payments/transactions
* v1/product-shelves/categories
* v1/product-shelves/categories/{id}/sub-categories
* v1/purchase-stamps
* v1/purchase-stamps/secret
* v1/purchase-stamps/secret/active
* v1/purchase-stamps/time
* v1/purchase-stamps/transactions
* v1/push-messages/messages/body
* v1/push-messages/push-tokens
* v1/receipts
* v1/receipts/{id}
* v1/slots
* v1/themepages
* v1/themepages/discover
* v1/themepages/foodfirst/discover
* v1/total-price/calculate
* v1/tracktrace/delivery-state-information
* v1/tracktrace/{orderId}/information
* v2/analytics
* v2/order/{orderId}
* v2/payments
* v2/payments/authorize
* v2/payments/cards
* v2/payments/cards/{id}
* v2/payments/options
* v2/payments/tokens
* v2/payments/tokens/{token}
* v2/payments/tokens/{token}/selected
* v2/pick-up-points/customer-locations
* v2/pick-up-points/{pupId}/opening-hours
* v2/receipts/{id}
* v2/recommendations/products/{webshopId}
* v2/webflow
* v4/order/invoice/download
* v4/order/summaries/first
* v4/order/{orderId}/actioncode
* v4/order/{orderId}/checkout
* v4/order/{orderId}/mov
* v4/order/{orderId}/receipt
* v4/order/{orderId}/sample
* v7/order/{orderId}/slot
* v8/order/summaries
* v8/order/{orderId}/details-grouped-by-taxonomy
* versioncheck/v2/{name}/{code}/check

## Jumbo

**BASE_URL:** `https://mobileapi.jumbo.com/`

GET

* autocomplete
* basket
* basket/checkout
* basket/fulfilment
* basket/oneclickcheckout
* basket/spending-limit
* basket/timeslot
* basket/validate/age
* categories
* configuration
* configuration/onboarding
* content-page/service/overview
* content-page/{pageKey}
* cross-sell-products
* homepage
* lists/carousel
* lists/favorites
* lists/following
* lists/jumbo-lists
* lists/labels
* lists/labels?inUseOnly=true
* lists/mylists
* lists/promoted-labels
* lists/promoted-lists
* lists/search
* lists/smart-lists/{smartListType}
* lists/userCreatedContainsSku/{sku}
* lists/{listId}
* lists/{listId}/containsSku/{sku}
* lists/{listId}/delisted-products
* lists/{listId}/following
* lists/{listId}/items
* maps/api/geocode/json
* ontent/{contentId}
* products
* products/{id}
* products/{id}/alternatives
* promotion-overview
* promotion-tabs
* promotion-tabs/{id}/{runtimeId}
* promotion/{id}
* recipe-lists/{listId}/items
* recipes
* recipes/{id}
* remindme
* search
* smulweb
* stores
* stores/slots
* users/address
* users/address/delivery
* users/me
* users/me/invoices
* users/me/orders
* users/me/orders/{orderId}
* users/me/orders/{orderId}/shipping-status
* users/me/orders/{orderId}/slots
* users/me/smart-lists
* users/me/social-lists
* users/me/social-lists-contains-product/{productSKU}
* users/me/social-lists/{listId}

POST

* basket/coupon
* basket/timeslot
* order/pricing
* recipe-lists/favorites/items
* users/me/orders/purchase
* users/me/orders/{orderId}
* users/me/social-lists
* users/me/social-lists/{listId}/list-items

### Picnic

**BASE_URL:** `https://storefront-prod.nl.picnicinternational.com/`

GET

* /api/{api_version}/user
* /api/{api_version}/cs-contact-info
* /public-api/{api_version}/cs-contact-info
* /api/{api_version}/cart
* /api/{api_version}/cart/delivery_slots
* /api/{api_version}/cart/checkout/order/{order_id}/status
* /api/{api_version}/consents/settings-page
* /api/{api_version}/consents
* /api/{api_version}/consents/general
* /api/{api_version}/consents/general/settings-page
* /api/{api_version}/deliveries/rateable
* /api/{api_version}/deliveries/{delivery_id}/scenario
* /api/{api_version}/deliveries/{delivery_id}/position
* /api/{api_version}/deliveries/{delivery_id}
* /api/{api_version}/content/faq
* /api/{api_version}/mgm
* /api/{api_version}/messages
* /api/{api_version}/my_store
* /api/{api_version}/product/{product_id}
* /api/{api_version}/suggest
* /api/{api_version}/search/
* /api/{api_version}/promotion/{promotionId}/category
* /api/{api_version}/recipes/{recipe_id}
* /api/{api_version}/reminders
* /api/{api_version}/content/search_empty_state
* /api/{api_version}/user-defined-bundles/{bundle_id}

POST

* /api/{api_version}/cart/add_orders
* /api/{api_version}/cart/add_product
* /api/{api_version}/cart/checkout/order/{order_id}/confirm
* /api/{api_version}/cart/clear
* /api/{api_version}/cart/products/add
* /api/{api_version}/cart/remove_group
* /api/{api_version}/cart/remove_product
* /api/{api_version}/cart/set_delivery_slot
* /api/{api_version}/deliveries/summary
* /api/{api_version}/deliveries/{delivery_id}/feedback
* /api/{api_version}/deliveries/{delivery_id}/issue-resolution-options
* /api/{api_version}/deliveries/{delivery_id}/rating
* /api/{api_version}/deliveries/{delivery_id}/resend_invoice_email
* /api/{api_version}/images/{context}
* /api/{api_version}/mgm/{mgmCode}/message
* /api/{api_version}/order/delivery/{delivery_id}/cancel
* /api/{api_version}/recipes/cart/recipe-article
* /api/{api_version}/recipes/cart/recipe-section
* /api/{api_version}/update_check
* /api/{api_version}/user-defined-bundles
* /api/{api_version}/user-products-blacklist
* /api/{api_version}/user/business_details
* /api/{api_version}/user/device/register_push
* /api/{api_version}/user/forgot_password
* /api/{api_version}/user/forgot_password/update
* /api/{api_version}/user/household_details
* /api/{api_version}/user/login
* /api/{api_version}/user/logout
* /api/{api_version}/user/phone_verification/generate
* /api/{api_version}/user/phone_verification/verify
* /api/{api_version}/user/register/direct
* /api/{api_version}/user/subscribe
* /api/{api_version}/user/suggestion

### ALDI

Categories -> https://webservice.aldi.nl/api/v1/products.json

Products -> https://webservice.aldi.nl/api/v1/products/brood-bakkerij/dagvers-brood.json

Details -> https://webservice.aldi.nl/api/v1/articles/products/brood-bakkerij/dagvers-brood/2152-1-0nl.json

GET

* Poi
* articles/{articleId}{region}.json
* articlesearch/{query}.json
* flyer.json
* index.json
* news.json
* productAlert/{token}
* products.json
* products/{category}.json
* promotions.json
* promotions/{promotionId}{region}.json
* recipedetail{path}.json
* recipes.json
* recipes/size={limit}.json
* recipesearch/{phrase}.json
* regions/{region}/inventories/{storeId}/inventory-items/{productId}
* shoppingList/{uuid}
* stage.json

POST

* .
* productAlert
* productAlert/{token}/phrases
* search
* shoppingList
* shoppingList/{listUuid}/entries

### COOP

Categories -> https://api.coop.nl/INTERSHOP/rest/WFS/COOP-COOPBase-Site/-/categories/FULL

Products -> https://api.coop.nl/INTERSHOP/rest/WFS/COOP-COOPBase-Site/-/categories/FULL/FULL-12/products

Details -> https://api.coop.nl/INTERSHOP/rest/WFS/COOP-COOPBase-Site/-/products/8717772024944

### LIDL

HAS NO PRODUCT DATA

### PLUS

Categories -> https://pls-sprmrkt-mw.prd.vdc1.plus.nl/api/v3/categorytree

Products -> https://pls-sprmrkt-mw.prd.vdc1.plus.nl/api/v3/navigation?tn_cid=168&tn_ps=1000

Details -> https://pls-sprmrkt-mw.prd.vdc1.plus.nl/api/v3/product/889494