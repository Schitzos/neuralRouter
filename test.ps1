$url = "http://localhost:8000/v1/chat/completions"

Write-Host "=== Test 1: Auto routing (classifier decides) ===" -ForegroundColor Cyan
$body = '{"model":"auto","messages":[{"role":"user","content":"What is 2+2?"}],"stream":false}'
$r = irm $url -Method POST -ContentType "application/json" -Body $body
Write-Host "Model used: $($r.model)"
Write-Host "Routing: $($r.x_schitzo.routing_method) | Tier: $($r.x_schitzo.tier)"
Write-Host "Answer: $($r.choices[0].message.content)"
Write-Host ""

Write-Host "=== Test 2: Bypass to Kimi/Moonshot ===" -ForegroundColor Cyan
$body = '{"model":"auto","messages":[{"role":"user","content":"use kimi to say hello in 5 words"}],"stream":false}'
$r = irm $url -Method POST -ContentType "application/json" -Body $body
Write-Host "Model used: $($r.model)"
Write-Host "Routing: $($r.x_schitzo.routing_method) | Tier: $($r.x_schitzo.tier)"
Write-Host "Answer: $($r.choices[0].message.content)"
Write-Host ""

Write-Host "=== Test 3: Bypass to Ollama ===" -ForegroundColor Cyan
$body = '{"model":"auto","messages":[{"role":"user","content":"use ollama to tell me a joke"}],"stream":false}'
$r = irm $url -Method POST -ContentType "application/json" -Body $body
Write-Host "Model used: $($r.model)"
Write-Host "Routing: $($r.x_schitzo.routing_method) | Tier: $($r.x_schitzo.tier)"
Write-Host "Answer: $($r.choices[0].message.content)"
Write-Host ""

Write-Host "=== Test 4: Direct Moonshot model ===" -ForegroundColor Cyan
$body = '{"model":"moonshot/moonshot-v1-8k","messages":[{"role":"user","content":"Hi!"}],"stream":false}'
$r = irm $url -Method POST -ContentType "application/json" -Body $body
Write-Host "Model used: $($r.model)"
Write-Host "Routing: $($r.x_schitzo.routing_method) | Tier: $($r.x_schitzo.tier)"
Write-Host "Answer: $($r.choices[0].message.content)"
Write-Host ""

Write-Host "=== Done! Check dashboard at http://localhost:5173 ===" -ForegroundColor Green
