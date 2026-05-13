
const cards = document.querySelectorAll('.card')

cards.forEach(card => {

    card.addEventListener('mousemove', e => {

        const rect = card.getBoundingClientRect()

        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        card.style.background = `
            radial-gradient(
                circle at ${x}px ${y}px,
                rgba(0,255,120,.15),
                rgba(255,255,255,.04)
            )
        `
    })

    card.addEventListener('mouseleave', () => {
        card.style.background = 'rgba(255,255,255,.05)'
    })

})
