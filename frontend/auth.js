const SUPABASE_URL = "https://jvmicjoprpsgjluupnck.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2bWljam9wcnBzZ2psdXVwbmNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxOTQzMjYsImV4cCI6MjA5NDc3MDMyNn0.WF7JNH_X-JO5CmprslS701ne5ZPBow5q4ysvjQAi-EU";

const client = supabase.createClient(
  SUPABASE_URL,
  SUPABASE_KEY
);

// ================= SIGNUP =================

async function signup(){

  const email = document.getElementById("email").value;

  const password = document.getElementById("password").value;

  const { error } = await client.auth.signUp({
    email,
    password
  });

  if(error){

    alert(error.message);

    return;
  }

  alert("Account created");

  window.location.href = "login.html";
}

// ================= LOGIN =================

async function login(){

  const email = document.getElementById("email").value;

  const password = document.getElementById("password").value;

  const { data, error } = await client.auth.signInWithPassword({
    email,
    password
  });

  if(error){

    alert(error.message);

    return;
  }

  localStorage.setItem(
    "eva_user",
    data.user.id
  );

  window.location.href = "index.html";
}
