from .models import ServiceTicket
from uuid import uuid4

def create_service_ticket(user, server):
    ticket_string = ''.join(str(uuid4()).split('-')) 
    ticket = ServiceTicket(service=server, user=user, ticket=ticket_string)
    ticket.save()
    return ticket_string