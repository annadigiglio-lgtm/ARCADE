package it.arcade;

import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.SecureRandom;
import java.util.*;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionTemplate;

/** Explicit local-only provisioning command; never enabled during normal startup. */
@Component
@ConditionalOnProperty(name="arcade.provision-demo",havingValue="true")
class DemoUsers implements ApplicationRunner {
    private final JdbcTemplate db;
    private final PasswordEncoder passwords;
    private final TransactionTemplate tx;
    DemoUsers(JdbcTemplate db,PasswordEncoder passwords,org.springframework.transaction.PlatformTransactionManager manager) {
        this.db=db; this.passwords=passwords; this.tx=new TransactionTemplate(manager);
    }
    @Override public void run(ApplicationArguments args) throws Exception {
        String url;
        try(var connection=db.getDataSource().getConnection()) { url=connection.getMetaData().getURL(); }
        if(!url.startsWith("jdbc:postgresql://localhost:") && !url.startsWith("jdbc:postgresql://127.0.0.1:"))
            throw new IllegalStateException("Creazione demo consentita solo sul database locale");
        var ids=db.queryForList("SELECT DISTINCT id_espositore FROM arcade.v_espositore_visite_ora WHERE edizione=2025 ORDER BY id_espositore LIMIT 2",String.class);
        if(ids.size()!=2) throw new IllegalStateException("Servono due espositori con visite 2025 nel database locale");
        Path output=Path.of("demo-accounts.local");
        // Reserve the credential file before changing the database. No overwrites.
        Files.createFile(output);
        try {
            tx.executeWithoutResult(status -> {
                try {
                    List<String> lines=new ArrayList<>();
                    lines.add("# Account DEMO locali. Non condividere o aggiungere a Git.");
                    for(int i=0;i<3;i++) {
                        String username=i==0?"staff.demo":"espositore.demo"+i;
                        byte[] random=new byte[18]; new SecureRandom().nextBytes(random);
                        String password=Base64.getUrlEncoder().withoutPadding().encodeToString(random);
                        db.update("INSERT INTO arcade.utente(username,password_hash,ruolo,id_espositore) VALUES (?,?,?,?)",username,passwords.encode(password),i==0?"STAFF":"ESPOSITORE",i==0?null:ids.get(i-1));
                        lines.add(username+"="+password);
                    }
                    Files.write(output,lines,StandardCharsets.UTF_8);
                } catch(java.io.IOException ex) { throw new java.io.UncheckedIOException(ex); }
            });
        } catch(Exception ex) { Files.deleteIfExists(output); throw ex; }
        System.out.println("Creati 3 utenti locali. Credenziali in api/demo-accounts.local (escluso da Git).");
    }
}
