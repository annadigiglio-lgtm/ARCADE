package it.arcade;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

@RestController
class AuthController {
    private final JdbcTemplate db;
    private final PasswordEncoder passwords;
    private final JwtEncoder tokens;
    private final String dummyHash;
    AuthController(JdbcTemplate db, PasswordEncoder passwords, JwtEncoder tokens) {
        this.db=db; this.passwords=passwords; this.tokens=tokens;
        dummyHash=passwords.encode(java.util.UUID.randomUUID().toString());
    }
    record Login(@NotBlank @Size(max=100) String username, @NotBlank @Size(max=72) String password) {
        @Override public String toString() { return "Login[credenziali riservate]"; }
    }
    @PostMapping("/auth/login")
    Map<String,Object> login(@Valid @RequestBody Login login) {
        var users=db.queryForList("SELECT id, password_hash, ruolo, id_espositore FROM arcade.utente WHERE username = ?",login.username());
        var user=users.isEmpty() ? null : users.getFirst();
        boolean valid=passwords.matches(login.password(),user==null ? dummyHash : (String)user.get("password_hash"));
        if (!valid || user==null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,"Credenziali non valide");
        Instant now=Instant.now();
        var claims=JwtClaimsSet.builder().issuer(SecurityConfig.ISSUER).subject(user.get("id").toString())
            .issuedAt(now).expiresAt(now.plusSeconds(3600)).claim("ruolo",user.get("ruolo"));
        if(user.get("id_espositore")!=null) claims.claim("idEspositore",user.get("id_espositore"));
        var token=tokens.encode(JwtEncoderParameters.from(JwsHeader.with(MacAlgorithm.HS256).build(),claims.build()));
        Map<String,Object> result=new LinkedHashMap<>();
        result.put("accessToken",token.getTokenValue()); result.put("tokenType","Bearer"); result.put("ruolo",user.get("ruolo"));
        if(user.get("id_espositore")!=null) result.put("idEspositore",user.get("id_espositore"));
        return result;
    }
}
