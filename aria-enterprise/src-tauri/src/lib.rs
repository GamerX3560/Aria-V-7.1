use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;
use std::process::Command;
use sysinfo::System;
use serde::Serialize;

// ─── Helpers ──────────────────────────────────────────
fn aria_dir() -> PathBuf { PathBuf::from("~/aria") }
fn read_json_file(path: &PathBuf) -> serde_json::Value {
    fs::read_to_string(path)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or(serde_json::json!({}))
}

// ─── Structs ──────────────────────────────────────────
#[derive(Serialize)] struct SysVitals { cpu_load: f32, ram_usage: u64, ram_total: u64 }
#[derive(Serialize)] struct SkillFile { name: String, size: u64, category: String, enabled: bool }

struct AppState { sys: Mutex<System> }

// ─── System Vitals ────────────────────────────────────
#[tauri::command]
fn get_sys_vitals(state: tauri::State<'_, AppState>) -> SysVitals {
    let mut sys = state.sys.lock().unwrap();
    sys.refresh_cpu_usage();
    sys.refresh_memory();
    SysVitals { cpu_load: sys.global_cpu_usage(), ram_usage: sys.used_memory(), ram_total: sys.total_memory() }
}

// ─── Skills (Real FS) ─────────────────────────────────
fn categorize_skill(name: &str) -> String {
    if name.contains("agent") { "Agent Protocol".into() }
    else if name.contains("research") || name.contains("deep_research") { "Research".into() }
    else if name.contains("browser") || name.contains("scraping") { "Web / Browser".into() }
    else if name.contains("security") || name.contains("password") { "Security".into() }
    else if name.contains("voice") || name.contains("speech") || name.contains("stt") { "Voice / Audio".into() }
    else if name.contains("android") || name.contains("adb") { "Mobile".into() }
    else if name.contains("media") || name.contains("image") || name.contains("screen") { "Media".into() }
    else if name.contains("system") || name.contains("terminal") || name.contains("desktop") || name.contains("clipboard") { "System".into() }
    else if name.contains("pdf") || name.contains("data") || name.contains("backup") { "Data / Files".into() }
    else { "General".into() }
}

#[tauri::command]
fn get_installed_skills() -> Vec<SkillFile> {
    let mut skills = Vec::new();
    let skills_dir = aria_dir().join("skills");
    if let Ok(entries) = fs::read_dir(&skills_dir) {
        for entry in entries.flatten() {
            if let Ok(file_name) = entry.file_name().into_string() {
                if file_name.starts_with("__") { continue; }
                let is_disabled = file_name.ends_with(".py.disabled");
                let is_py = file_name.ends_with(".py") || is_disabled;
                if is_py {
                    let size = entry.metadata().map(|m| m.len()).unwrap_or(0);
                    let base = file_name.replace(".disabled", "");
                    let cat = categorize_skill(&base);
                    skills.push(SkillFile { name: file_name, size, category: cat, enabled: !is_disabled });
                }
            }
        }
    }
    skills.sort_by(|a, b| a.name.cmp(&b.name));
    skills
}

#[tauri::command]
fn read_skill_source(name: String) -> Result<String, String> {
    let p = aria_dir().join("skills").join(&name);
    fs::read_to_string(&p).map_err(|e| format!("Cannot read {}: {}", name, e))
}

#[tauri::command]
fn write_skill_source(name: String, content: String) -> Result<String, String> {
    let p = aria_dir().join("skills").join(&name);
    fs::write(&p, &content).map_err(|e| format!("Cannot write {}: {}", name, e))?;
    Ok(format!("Saved {}", name))
}

#[tauri::command]
fn delete_skill(name: String) -> Result<String, String> {
    let p = aria_dir().join("skills").join(&name);
    fs::remove_file(&p).map_err(|e| format!("Cannot delete {}: {}", name, e))?;
    Ok(format!("Deleted {}", name))
}

#[tauri::command]
fn toggle_skill(name: String) -> Result<String, String> {
    let skills_dir = aria_dir().join("skills");
    if name.ends_with(".disabled") {
        let new_name = name.replace(".disabled", "");
        fs::rename(skills_dir.join(&name), skills_dir.join(&new_name))
            .map_err(|e| format!("Cannot enable: {}", e))?;
        Ok(format!("Enabled {}", new_name))
    } else {
        let new_name = format!("{}.disabled", name);
        fs::rename(skills_dir.join(&name), skills_dir.join(&new_name))
            .map_err(|e| format!("Cannot disable: {}", e))?;
        Ok(format!("Disabled {}", name))
    }
}

#[tauri::command]
fn import_skill(name: String, content: String) -> Result<String, String> {
    let fname = if name.ends_with(".py") { name.clone() } else { format!("{}.py", name) };
    let p = aria_dir().join("skills").join(&fname);
    if p.exists() { return Err(format!("{} already exists", fname)); }
    fs::write(&p, &content).map_err(|e| format!("Cannot create {}: {}", fname, e))?;
    Ok(format!("Created {}", fname))
}

// ─── Memory (Real memory.json) ────────────────────────
#[tauri::command]
fn get_memory_entries() -> serde_json::Value {
    let p = aria_dir().join("memory.json");
    read_json_file(&p)
}

#[tauri::command]
fn get_memory_size() -> u64 {
    let p = aria_dir().join("memory.json");
    fs::metadata(&p).map(|m| m.len()).unwrap_or(0)
}

#[tauri::command]
fn save_memory_entry(key: String, value: String, entry_type: String) -> Result<String, String> {
    let p = aria_dir().join("memory.json");
    let mut data = read_json_file(&p);
    if let Some(obj) = data.as_object_mut() {
        obj.insert(key.clone(), serde_json::json!({
            "value": value, "type": entry_type,
            "timestamp": std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_millis() as u64
        }));
    } else {
        data = serde_json::json!({ &key: { "value": value, "type": entry_type } });
    }
    fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
        .map_err(|e| format!("Cannot save memory: {}", e))?;
    Ok(format!("Saved memory entry '{}'", key))
}

#[tauri::command]
fn delete_memory_entry(key: String) -> Result<String, String> {
    let p = aria_dir().join("memory.json");
    let mut data = read_json_file(&p);
    if let Some(obj) = data.as_object_mut() {
        obj.remove(&key);
        fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
            .map_err(|e| format!("Cannot write: {}", e))?;
    }
    Ok(format!("Deleted '{}'", key))
}

// ─── Config (Real config.yaml / identity.yaml) ───────
#[tauri::command]
fn get_aria_config() -> serde_json::Value {
    let p = aria_dir().join("config.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    // Parse YAML as simple key:value pairs
    let mut map = serde_json::Map::new();
    for line in content.lines() {
        if let Some((k, v)) = line.split_once(':') {
            let k = k.trim().to_string();
            let v = v.trim().trim_matches('"').trim_matches('\'').to_string();
            map.insert(k, serde_json::Value::String(v));
        }
    }
    serde_json::Value::Object(map)
}

#[tauri::command]
fn save_aria_config(data: serde_json::Value) -> Result<String, String> {
    let p = aria_dir().join("config.yaml");
    let mut lines = Vec::new();
    if let Some(obj) = data.as_object() {
        for (k, v) in obj {
            let val = match v { serde_json::Value::String(s) => s.clone(), _ => v.to_string() };
            lines.push(format!("{}: {}", k, val));
        }
    }
    fs::write(&p, lines.join("\n")).map_err(|e| format!("Cannot save config: {}", e))?;
    Ok("Config saved".into())
}

#[tauri::command]
fn get_identity() -> serde_json::Value {
    let p = aria_dir().join("identity.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    let mut map = serde_json::Map::new();
    for line in content.lines() {
        if let Some((k, v)) = line.split_once(':') {
            let k = k.trim().to_string();
            let v = v.trim().trim_matches('"').trim_matches('\'').to_string();
            if !k.starts_with('#') && !k.is_empty() {
                map.insert(k, serde_json::Value::String(v));
            }
        }
    }
    serde_json::Value::Object(map)
}

#[tauri::command]
fn save_identity(data: serde_json::Value) -> Result<String, String> {
    let p = aria_dir().join("identity.yaml");
    let mut lines = Vec::new();
    if let Some(obj) = data.as_object() {
        for (k, v) in obj {
            let val = match v { serde_json::Value::String(s) => s.clone(), _ => v.to_string() };
            lines.push(format!("{}: \"{}\"", k, val));
        }
    }
    fs::write(&p, lines.join("\n")).map_err(|e| format!("Cannot save identity: {}", e))?;
    Ok("Identity saved".into())
}

// ─── Credentials (Real vault/) ────────────────────────
#[tauri::command]
fn get_credentials() -> serde_json::Value {
    let p = aria_dir().join("vault").join("credentials.json");
    if !p.exists() {
        let p2 = aria_dir().join("vault.example.json");
        return read_json_file(&p2);
    }
    read_json_file(&p)
}

#[tauri::command]
fn save_credentials(data: serde_json::Value) -> Result<String, String> {
    let dir = aria_dir().join("vault");
    let _ = fs::create_dir_all(&dir);
    let p = dir.join("credentials.json");
    fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
        .map_err(|e| format!("Cannot save vault: {}", e))?;
    Ok("Credentials saved".into())
}

// ─── Agents (from config) ─────────────────────────────
#[tauri::command]
fn get_agents() -> serde_json::Value {
    let p = aria_dir().join("agents.json");
    if p.exists() {
        return read_json_file(&p);
    }
    // Return default agent roster if no file
    serde_json::json!([
        { "id": "master", "name": "ARIA Master Router", "model": "qwen2.5-coder-32b", "status": "ONLINE", "role": "Supervisor", "icon": "🌍", "systemPrompt": "You are ARIA, the master coordinator." },
        { "id": "research", "name": "Deep Research v4", "model": "scrapling/playwright", "status": "ONLINE", "role": "Web Drone", "icon": "🔍", "systemPrompt": "You are a research agent." },
        { "id": "browser", "name": "Browser Agent", "model": "browser-use/chromium", "status": "ONLINE", "role": "Autonomous Browser", "icon": "🌐", "systemPrompt": "You are a browser automation agent." },
        { "id": "voice", "name": "Voice Operator", "model": "piper/espeak", "status": "STANDBY", "role": "Communications", "icon": "🎙️", "systemPrompt": "You handle voice I/O." },
        { "id": "desktop", "name": "Desktop Daemon", "model": "ydotool/wayland", "status": "ONLINE", "role": "System Control", "icon": "🖥️", "systemPrompt": "You control desktop input." },
        { "id": "mesh", "name": "Mesh Coordinator", "model": "fastapi/cloudflared", "status": "ONLINE", "role": "Inter-ARIA Network", "icon": "🕸️", "systemPrompt": "You manage mesh peers." }
    ])
}

#[tauri::command]
fn save_agents(data: serde_json::Value) -> Result<String, String> {
    let p = aria_dir().join("agents.json");
    fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
        .map_err(|e| format!("Cannot save agents: {}", e))?;
    Ok("Agents saved".into())
}

// ─── Logs ─────────────────────────────────────────────
#[tauri::command]
fn get_logs(count: usize) -> Vec<String> {
    if let Ok(out) = Command::new("journalctl")
        .args(["--user", "-u", "jarvis.service", "-n", &count.to_string(), "--no-pager", "-o", "cat"])
        .output() {
        let lines: Vec<String> = String::from_utf8_lossy(&out.stdout).lines().map(|s| s.into()).collect();
        if lines.is_empty() || (lines.len() == 1 && lines[0].is_empty()) {
            return vec!["[INFO] No jarvis.service logs found. Service may not be running.".into()];
        }
        lines
    } else {
        vec!["[ERROR] Failed to read journalctl logs".into()]
    }
}

// ─── Mesh Status ──────────────────────────────────────
#[tauri::command]
fn get_mesh_status() -> serde_json::Value {
    // Try to reach the mesh API
    if let Ok(out) = Command::new("curl")
        .args(["-s", "--max-time", "2", "http://localhost:8741/aria/status"])
        .output() {
        let body = String::from_utf8_lossy(&out.stdout);
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(&body) {
            return v;
        }
    }
    serde_json::json!({ "peers": 0, "public_url": null, "status": "offline" })
}

// ─── Browser Agent Status ─────────────────────────────
#[tauri::command]
fn get_browser_status() -> serde_json::Value {
    // Check if chromium/playwright process is running
    let chromium_running = Command::new("pgrep").args(["-f", "chromium"]).output()
        .map(|o| o.status.success()).unwrap_or(false);
    let playwright_running = Command::new("pgrep").args(["-f", "playwright"]).output()
        .map(|o| o.status.success()).unwrap_or(false);

    serde_json::json!({
        "layer1_scrapling": "Available",
        "layer2_browseruse": if chromium_running { "Active" } else { "Idle" },
        "layer3_playwright": if playwright_running { "Active" } else { "Idle" },
        "status": if chromium_running || playwright_running { "ACTIVE" } else { "IDLE" }
    })
}

// ─── Service Control ──────────────────────────────────
#[tauri::command]
fn get_service_status() -> String {
    if let Ok(out) = Command::new("systemctl").args(["--user", "is-active", "jarvis.service"]).output() {
        String::from_utf8_lossy(&out.stdout).trim().into()
    } else { "unknown".into() }
}

#[tauri::command]
fn restart_aria_service() -> Result<String, String> {
    Command::new("systemctl").args(["--user", "restart", "jarvis.service"]).spawn()
        .map_err(|e| format!("Cannot restart: {}", e))?;
    Ok("ARIA service restarting...".into())
}

#[tauri::command]
fn stop_aria_service() -> Result<String, String> {
    Command::new("systemctl").args(["--user", "stop", "jarvis.service"]).spawn()
        .map_err(|e| format!("Cannot stop: {}", e))?;
    Ok("ARIA service stopped".into())
}

#[tauri::command]
fn run_self_test() -> String {
    // Actually check critical components
    let mut results = Vec::new();
    let check_file = |name: &str, path: PathBuf| -> String {
        if path.exists() { format!("✅ {} found", name) } else { format!("❌ {} missing", name) }
    };
    results.push(check_file("config.yaml", aria_dir().join("config.yaml")));
    results.push(check_file("identity.yaml", aria_dir().join("identity.yaml")));
    results.push(check_file("memory.json", aria_dir().join("memory.json")));
    results.push(check_file("agent_loop.py", aria_dir().join("core/agent_loop.py")));
    results.push(check_file("skills/", aria_dir().join("skills")));

    let svc = get_service_status();
    results.push(format!("{} jarvis.service: {}", if svc == "active" { "✅" } else { "⚠️" }, svc));

    results.join("\n")
}

// ─── Voice Config ─────────────────────────────────────
#[tauri::command]
fn get_voice_config() -> serde_json::Value {
    let p = aria_dir().join("identity.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    let mut backend = "piper".to_string();
    let mut speed = "1.0".to_string();
    let mut pitch = "1.0".to_string();
    for line in content.lines() {
        if let Some((k, v)) = line.split_once(':') {
            let k = k.trim();
            let v = v.trim().trim_matches('"').trim_matches('\'');
            match k {
                "tts_backend" | "voice_backend" => backend = v.into(),
                "voice_speed" | "tts_speed" => speed = v.into(),
                "voice_pitch" | "tts_pitch" => pitch = v.into(),
                _ => {}
            }
        }
    }
    serde_json::json!({ "backend": backend, "speed": speed, "pitch": pitch })
}

#[tauri::command]
fn save_voice_config(backend: String, speed: String, pitch: String) -> Result<String, String> {
    // Read existing identity.yaml or create
    let p = aria_dir().join("identity.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    // Remove old voice lines
    let lines: Vec<&str> = content.lines()
        .filter(|l| !l.starts_with("tts_backend:") && !l.starts_with("voice_backend:") && !l.starts_with("voice_speed:") && !l.starts_with("tts_speed:") && !l.starts_with("voice_pitch:") && !l.starts_with("tts_pitch:"))
        .collect();
    let mut new_content = lines.join("\n");
    new_content.push_str(&format!("\ntts_backend: \"{}\"\nvoice_speed: \"{}\"\nvoice_pitch: \"{}\"", backend, speed, pitch));
    fs::write(&p, new_content).map_err(|e| format!("Cannot save voice config: {}", e))?;
    Ok("Voice config saved".into())
}

#[tauri::command]
fn test_voice(text: String) -> Result<String, String> {
    let _ = Command::new("bash").args(["-c", &format!("echo '{}' | piper --model ~/aria/voice/models/*.onnx --output_file /tmp/aria_tts_test.wav 2>/dev/null && aplay /tmp/aria_tts_test.wav 2>/dev/null || espeak '{}'", text, text)])
        .spawn().map_err(|e| format!("TTS failed: {}", e))?;
    Ok("Playing audio...".into())
}

// ─── Personality ──────────────────────────────────────
#[tauri::command]
fn get_personality() -> serde_json::Value {
    let p = aria_dir().join("identity.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    let mut formality = 50;
    let mut verbosity = 50;
    let mut playfulness = 50;
    for line in content.lines() {
        if let Some((k, v)) = line.split_once(':') {
            let k = k.trim();
            let v = v.trim().trim_matches('"').trim_matches('\'');
            match k {
                "formality" => formality = v.parse().unwrap_or(50),
                "verbosity" => verbosity = v.parse().unwrap_or(50),
                "playfulness" => playfulness = v.parse().unwrap_or(50),
                _ => {}
            }
        }
    }
    serde_json::json!({ "formality": formality, "verbosity": verbosity, "playfulness": playfulness })
}

#[tauri::command]
fn save_personality(formality: u32, verbosity: u32, playfulness: u32) -> Result<String, String> {
    let p = aria_dir().join("identity.yaml");
    let content = fs::read_to_string(&p).unwrap_or_default();
    let lines: Vec<&str> = content.lines()
        .filter(|l| !l.starts_with("formality:") && !l.starts_with("verbosity:") && !l.starts_with("playfulness:"))
        .collect();
    let mut new_content = lines.join("\n");
    new_content.push_str(&format!("\nformality: {}\nverbosity: {}\nplayfulness: {}", formality, verbosity, playfulness));
    fs::write(&p, new_content).map_err(|e| format!("Cannot save personality: {}", e))?;
    Ok("Personality saved".into())
}

// ─── Devices ──────────────────────────────────────────
#[tauri::command]
fn get_devices() -> serde_json::Value {
    let p = aria_dir().join("devices.json");
    if p.exists() { return read_json_file(&p); }
    // Detect connected ADB devices
    let mut devices = Vec::new();
    if let Ok(out) = Command::new("adb").args(["devices", "-l"]).output() {
        let output = String::from_utf8_lossy(&out.stdout);
        for line in output.lines().skip(1) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 && parts[1] == "device" {
                devices.push(serde_json::json!({
                    "name": format!("Android ({})", parts[0]), "icon": "📱",
                    "conn": format!("ADB {}", parts[0]), "status": "Active", "type": "android"
                }));
            }
        }
    }
    serde_json::json!(devices)
}

#[tauri::command]
fn save_devices(data: serde_json::Value) -> Result<String, String> {
    let p = aria_dir().join("devices.json");
    fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
        .map_err(|e| format!("Cannot save devices: {}", e))?;
    Ok("Devices saved".into())
}

// ─── Scrape URL ───────────────────────────────────────
#[tauri::command]
fn scrape_url(url: String) -> Result<String, String> {
    let script = format!(
        "import trafilatura; r = trafilatura.fetch_url('{}'); print(trafilatura.extract(r) if r else 'Failed to fetch')",
        url.replace("'", "\\'")
    );
    match Command::new("python3").args(["-c", &script]).output() {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
            if out.status.success() && !stdout.trim().is_empty() {
                Ok(stdout)
            } else {
                Err(format!("Scrape failed: {}", if stderr.is_empty() { "Empty result" } else { &stderr }))
            }
        }
        Err(e) => Err(format!("Cannot run scraper: {}", e)),
    }
}

// ─── Execute Shell Command ────────────────────────────
#[tauri::command]
fn execute_shell(cmd: String) -> Result<String, String> {
    match Command::new("bash").args(["-c", &cmd]).output() {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
            Ok(format!("{}{}", stdout, if stderr.is_empty() { String::new() } else { format!("\n[stderr] {}", stderr) }))
        }
        Err(e) => Err(format!("Execution error: {}", e)),
    }
}

// ─── Flush Cache ──────────────────────────────────────
#[tauri::command]
fn flush_cache() -> Result<String, String> {
    // Clear temporary memory entries
    let p = aria_dir().join("memory.json");
    if p.exists() {
        let data = read_json_file(&p);
        if let Some(obj) = data.as_object() {
            let filtered: serde_json::Map<String, serde_json::Value> = obj.iter()
                .filter(|(_k, v)| v.get("type").and_then(|t| t.as_str()) != Some("session"))
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect();
            let _ = fs::write(&p, serde_json::to_string_pretty(&serde_json::Value::Object(filtered)).unwrap_or_default());
        }
    }
    // Clear Python __pycache__
    let _ = Command::new("find").args([aria_dir().to_str().unwrap(), "-type", "d", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"]).spawn();
    Ok("Cache flushed: cleared session memory and __pycache__".into())
}

// ─── Security Config ──────────────────────────────────
#[tauri::command]
fn get_security_config() -> serde_json::Value {
    let p = aria_dir().join("security.json");
    if p.exists() { return read_json_file(&p); }
    serde_json::json!({
        "sudo_lock": false,
        "confirm_mode": true,
        "network_egress": true,
        "blocklist": ["rm -rf /", "mkfs.*", "dd if=.*", ":(){ :|:& };:"],
        "sandbox": ["~/aria/*", "/home/gamerx/.gemini/*", "/tmp/aria_workspace/*"]
    })
}

#[tauri::command]
fn save_security_config(data: serde_json::Value) -> Result<String, String> {
    let p = aria_dir().join("security.json");
    fs::write(&p, serde_json::to_string_pretty(&data).unwrap_or_default())
        .map_err(|e| format!("Cannot save security config: {}", e))?;
    Ok("Security config saved".into())
}

// ─── App Entry Point ──────────────────────────────────
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState { sys: Mutex::new(System::new_all()) })
        .invoke_handler(tauri::generate_handler![
            get_sys_vitals, get_installed_skills, read_skill_source, write_skill_source,
            delete_skill, toggle_skill, import_skill,
            get_memory_entries, get_memory_size, save_memory_entry, delete_memory_entry,
            get_aria_config, save_aria_config, get_identity, save_identity,
            get_credentials, save_credentials,
            get_agents, save_agents,
            get_logs, get_mesh_status, get_browser_status,
            get_service_status, restart_aria_service, stop_aria_service,
            run_self_test, flush_cache,
            get_voice_config, save_voice_config, test_voice,
            get_personality, save_personality,
            get_devices, save_devices,
            scrape_url, execute_shell,
            get_security_config, save_security_config
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
