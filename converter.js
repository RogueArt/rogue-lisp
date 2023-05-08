const str = `
(class main
 (field x null)
 (field y null)
 (field z "bark")
 (method main ()
   (begin
     (set x (new dog))
     (set y (call x bark z))
     (print y)
   )
 )
)

(class dog
  (method bark (x)
    (begin
      (print x)
      (return "woof")
    )
  )
)

`

const lines = str.split('\n')
const trimmed = lines.map(str => str.trim())
const filtered = trimmed.filter(str => str.length > 0)
console.log(filtered)
