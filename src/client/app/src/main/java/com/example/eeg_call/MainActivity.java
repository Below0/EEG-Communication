package com.example.eeg_call;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.Manifest;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.provider.ContactsContract;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.InstanceIdResult;

import org.json.JSONObject;
import org.w3c.dom.Text;

import java.util.concurrent.ExecutionException;

public class MainActivity extends AppCompatActivity {
    public static SharedPreferences sf;
    public static SharedPreferences.Editor editor;
    private boolean isRegistered;
    private LinearLayout frame1;
    private ImageView btn;
    private TextView textView;
    private String token;
    private EditText editText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        sf = getSharedPreferences("config",MODE_PRIVATE);
        editor = sf.edit();
        initFCM();
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        frame1 = (LinearLayout)findViewById(R.id.layout1);
        btn = (ImageView) findViewById(R.id.button);
        btn.setOnClickListener(new MyClickListener());
        textView = (TextView)findViewById(R.id.token);
        editText = (EditText)findViewById(R.id.input);
    }

    public void initFCM(){
        FirebaseInstanceId.getInstance().getInstanceId()
                .addOnCompleteListener(new OnCompleteListener<InstanceIdResult>() {
                    @Override
                    public void onComplete(@NonNull Task<InstanceIdResult> task) {
                        if (!task.isSuccessful()){
                            Log.w("FCM","getInstanceID failed", task.getException());
                            return;
                        }
                        token = task.getResult().getToken();
                        textView.setText(token);
                        Log.d("FCM", "Token : " + token);
                        checkRegister();
                    }
                });
    }

    public void checkRegister(){

        isRegistered = sf.getBoolean("check",false);
        if(isRegistered == false){
            frame1.setVisibility(View.VISIBLE);
            textView.setVisibility(View.INVISIBLE);
            Log.d("debug","register false");
        }
        else{
            frame1.setVisibility(View.INVISIBLE);
            textView.setVisibility(View.VISIBLE);
            Log.d("debug","register true");
        }
    }

    class MyClickListener implements View.OnClickListener{
        @Override
        public void onClick(View v) {
            JSONObject obj;
            String id = "0";
            String name = editText.getText().toString();
//                http://44.233.139.129:8000/callee/
            if(name.isEmpty()){
                Toast.makeText(getApplicationContext(),"이름을 입력해주세요",Toast.LENGTH_SHORT).show();
                return;
            }
            try {
                ServerInterface task = new ServerInterface(getApplicationContext());
                task.execute("http://44.233.139.129:8000/callee/", "token",token, "name",name);
                String callBackValue = task.get();
                try {

                    obj = new JSONObject(callBackValue);
                    id = obj.getString("id");
                    Log.d("My App", obj.toString());

                } catch (Throwable t) {
                    Log.e("My App", "Could not parse malformed JSON: \"" + callBackValue + "\"");
                }

                // fail
                if(callBackValue.isEmpty() || callBackValue.equals("") || callBackValue == null || callBackValue.contains("Error")) {
                    Toast.makeText(getApplicationContext(), name, Toast.LENGTH_SHORT).show();
                }
                // success
                else {
                    editor.putBoolean("check",true);
                    editor.commit();
                    textView.setText(id);
                    // TODO : callBackValue를 이용해서 코드기술
                }
                checkRegister();

            } catch (ExecutionException e) {

                e.printStackTrace();
                Log.d("POST", "ExecutionException");
            } catch (InterruptedException e) {
                e.printStackTrace();
                Log.d("POST", "InterruptedException");

            }
        }
    }

}
