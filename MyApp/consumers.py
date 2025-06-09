from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from MyApp.models import Order, CustomToken
import json



class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from urllib.parse import parse_qs

        self.user = await self.get_user()
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

        query_params = parse_qs(self.scope['query_string'].decode())
        page = query_params.get('page', ['1'])[0] or '1'
        page_size = query_params.get('page_size', ['10'])[0] or '10'
        is_paid = query_params.get('is_paid', [None])[0]
        order_id = query_params.get('order_id', [None])[0]

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            page_size = 10

        if is_paid is not None:
            is_paid = is_paid.lower() == 'true'
        if order_id is not None:
            try:
                order_id = int(order_id)
            except (TypeError, ValueError):
                order_id = None

        orders = await self.get_orders(self.user, page, page_size, is_paid, order_id)
        await self.send_json({"orders": orders})
        
        await self.channel_layer.group_send("orders", {
            "type": "send_order_notification",
            "data": orders
        })
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orders", self.channel_name)

    async def receive(self, text_data):
        if isinstance(self.user, AnonymousUser):
            await self.send_json({"error": "Unauthorized"})
            return

        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "send_message":
                message = data.get("message")
                if message:
                    await self.channel_layer.group_send("orders", {
                        "type": "send_order_notification",
                        "data": message
                    })
                else:
                    await self.send_json({"error": "Missing 'message' key"})

            else:
                await self.send_json({"error": "Invalid action"})

        except json.JSONDecodeError as e:
            await self.send_json({"error": "Invalid JSON", "details": str(e)})

        except Exception as e:
            await self.send_json({"error": "Server error", "details": str(e)})

    async def send_order_notification(self, event):
        await self.send_json({"notification": event.get("data")})

    @database_sync_to_async
    def get_user(self):
        token_key = self.scope['query_string'].decode().split('token=')[-1]
        try:
            token = CustomToken.objects.get(key=token_key)
            return token.user if token.is_valid() else AnonymousUser()

        except CustomToken.DoesNotExist:
            return AnonymousUser()

    @database_sync_to_async
    def get_orders(self, user, page=1, page_size=10, is_paid=None, order_id=None):
        orders = Order.objects.filter(customer_name=user)

        if is_paid is not None:
            if str(is_paid).lower() == 'true':
                orders = orders.filter(is_paid=True)

            elif str(is_paid).lower() == 'false':
                orders = orders.filter(is_paid=False)

        if order_id:
            orders = orders.filter(id=order_id)

        paginator = Paginator(orders, page_size)
        page_obj = paginator.get_page(page)

        result = []
        for order in page_obj:
            items = []
            for item in order.ordered_items.all():
                item_data = {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'qty': item.qty,
                    'price': float(item.price)
                }
                items.append(item_data)

            result.append({
                'order_id': order.id,
                'customer_name': order.customer_name,
                'status': order.status,
                'is_paid': order.is_paid,
                'created_at': order.created_at.isoformat(),
                'items': items,
                'total': float(order.total_amount())
            })

        return {
            'orders': result,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_orders': paginator.count
        }

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
