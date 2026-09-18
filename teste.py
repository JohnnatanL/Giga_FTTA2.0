import reflex as rx

class teste(rx.State):
    pass

def index():
    return rx.heading("teste")

app = rx.App()
app.add_page(index)

app.run()