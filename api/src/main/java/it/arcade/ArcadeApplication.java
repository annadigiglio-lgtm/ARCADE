package it.arcade;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ArcadeApplication {
    public static void main(String[] args) {
        var context=SpringApplication.run(ArcadeApplication.class, args);
        if(context.getEnvironment().getProperty("arcade.provision-demo",Boolean.class,false)) context.close();
    }
}
